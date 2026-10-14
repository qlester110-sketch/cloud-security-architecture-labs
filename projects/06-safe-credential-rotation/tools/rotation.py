"""Local credential lifecycle lab. Never connect this store to real accounts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import tempfile


class RotationLab:
    """Durable single-host model of a provider, vault, rotator and consumers."""

    def __init__(self, path):
        path = Path(path)
        # Reject symlinks and create with owner-only permissions before opening SQLite.
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        os.fchmod(fd, 0o600)
        os.close(fd)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS credentials
              (version INTEGER PRIMARY KEY, token TEXT, digest TEXT, valid INTEGER);
            CREATE TABLE IF NOT EXISTS lifecycle
              (id INTEGER PRIMARY KEY CHECK(id=1), current INTEGER, previous INTEGER,
               pending INTEGER, stage TEXT, deadline INTEGER);
            CREATE TABLE IF NOT EXISTS workers
              (name TEXT PRIMARY KEY, version INTEGER, heartbeat INTEGER);
            CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS audit
              (id INTEGER PRIMARY KEY, event TEXT, version INTEGER);
        """)
        if not self.db.execute("SELECT 1 FROM lifecycle").fetchone():
            with self.db:
                self._credential(1)
                self.db.execute("INSERT INTO lifecycle VALUES(1,1,NULL,NULL,'idle',NULL)")

    def close(self):
        self.db.close()

    def state(self):
        return dict(self.db.execute("SELECT * FROM lifecycle").fetchone())

    def _credential(self, version):
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        self.db.execute("INSERT INTO credentials VALUES(?,?,?,1)", (version, token, digest))

    def _event(self, event, version):
        self.db.execute("INSERT INTO audit(event,version) VALUES(?,?)", (event, version))

    def token(self, version):
        row = self.db.execute("SELECT token FROM credentials WHERE version=?", (version,)).fetchone()
        return row[0] if row else None

    def accepts(self, token):
        if not isinstance(token, str):
            return False
        digest = hashlib.sha256(token.encode()).hexdigest()
        row = self.db.execute("SELECT valid FROM credentials WHERE digest=?", (digest,)).fetchone()
        return bool(row and row[0])

    def register(self, name, now):
        with self.db:
            if self.state()['stage'] != 'idle':
                raise RuntimeError('worker enrollment is frozen during rotation')
            self.db.execute("INSERT INTO workers VALUES(?,?,?)", (name, self.state()['current'], now))

    def refresh(self, name, now):
        with self.db:
            cursor = self.db.execute("UPDATE workers SET version=?,heartbeat=? WHERE name=?",
                                     (self.state()['current'], now, name))
            if cursor.rowcount != 1:
                raise ValueError('unknown worker')

    def process(self, name, order_id):
        """Authenticate before an idempotent synthetic order side effect."""
        row = self.db.execute("SELECT version FROM workers WHERE name=?", (name,)).fetchone()
        if not row:
            raise ValueError('unknown worker')
        if not self.accepts(self.token(row[0])):
            raise PermissionError('credential rejected')
        with self.db:
            cursor = self.db.execute("INSERT OR IGNORE INTO orders VALUES(?)", (order_id,))
        return cursor.rowcount == 1

    def prepare(self):
        with self.db:
            # A write lock serializes competing controllers, including separate processes.
            self.db.execute('BEGIN IMMEDIATE')
            state = self.state()
            if state['stage'] != 'idle':
                raise RuntimeError('rotation already in progress')
            version = self.db.execute('SELECT MAX(version)+1 FROM credentials').fetchone()[0]
            self._credential(version)
            self.db.execute("UPDATE lifecycle SET pending=?,stage='prepared'", (version,))
            self._event('prepared', version)
        return version

    def validate(self, healthy=True):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            state = self.state()
            if state['stage'] != 'prepared':
                raise RuntimeError('prepare before validation')
            if not healthy or not self.accepts(self.token(state['pending'])):
                self.db.execute('UPDATE credentials SET valid=0,token=NULL WHERE version=?',
                                (state['pending'],))
                self._event('validation_failed', state['pending'])
                self.db.execute("UPDATE lifecycle SET pending=NULL,stage='idle'")
                return False
            self.db.execute("UPDATE lifecycle SET stage='validated'")
            self._event('validated', state['pending'])
        return True

    def promote(self, now, grace=30):
        if grace <= 0:
            raise ValueError('grace must be positive')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            state = self.state()
            if state['stage'] != 'validated':
                raise RuntimeError('validate before promotion')
            self.db.execute("UPDATE lifecycle SET previous=current,current=pending,pending=NULL,"
                            "stage='promoted',deadline=?", (now + grace,))
            self._event('promoted', state['pending'])

    def retire(self, now, heartbeat_ttl=15):
        if heartbeat_ttl <= 0:
            raise ValueError('heartbeat TTL must be positive')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            state = self.state()
            if state['stage'] != 'promoted':
                raise RuntimeError('no promoted rotation')
            workers = self.db.execute('SELECT * FROM workers').fetchall()
            ready = bool(workers) and all(w['version'] == state['current'] and
                        0 <= now - w['heartbeat'] <= heartbeat_ttl for w in workers)
            if ready:
                self.db.execute('UPDATE credentials SET valid=0,token=NULL WHERE version=?',
                                (state['previous'],))
                self._event('retired', state['previous'])
                self.db.execute("UPDATE lifecycle SET previous=NULL,deadline=NULL,stage='idle'")
                return 'retired'
            if now >= state['deadline']:
                # Cut back, refresh all configured local consumers, revoke failed generation.
                self.db.execute('UPDATE workers SET version=?,heartbeat=?', (state['previous'], now))
                self.db.execute('UPDATE credentials SET valid=0,token=NULL WHERE version=?',
                                (state['current'],))
                self._event('rolled_back', state['current'])
                self.db.execute("UPDATE lifecycle SET current=previous,previous=NULL,deadline=NULL,stage='idle'")
                return 'rolled_back'
            return 'waiting'

    def report(self):
        return {'stage': self.state()['stage'], 'current_version': self.state()['current'],
                'orders_processed': self.db.execute('SELECT COUNT(*) FROM orders').fetchone()[0],
                'valid_credentials': self.db.execute('SELECT COUNT(*) FROM credentials WHERE valid=1').fetchone()[0],
                'audit': [dict(r) for r in self.db.execute('SELECT event,version FROM audit ORDER BY id')]}


def demo(scenario):
    with tempfile.TemporaryDirectory(prefix='credential-lab-') as directory:
        lab = RotationLab(Path(directory) / 'lab.sqlite')
        try:
            for name in ('orders', 'inventory', 'notifications'):
                lab.register(name, 0)
            completed = 0
            failed = 0
            outcome = None
            for tick in range(100):
                if tick == 30:
                    lab.prepare()
                    if lab.validate(healthy=scenario != 'failed-validation'):
                        lab.promote(tick, grace=20)
                if tick >= 35:
                    for name in ('orders', 'inventory', 'notifications'):
                        if scenario != 'stale-worker' or name != 'notifications':
                            lab.refresh(name, tick)
                for name in ('orders', 'inventory', 'notifications'):
                    try:
                        completed += lab.process(name, f'{name}-{tick}')
                    except PermissionError:
                        failed += 1
                if lab.state()['stage'] == 'promoted':
                    outcome = lab.retire(tick)
            report = lab.report()
            report.update(scenario=scenario, operations_attempted=300,
                          successful_operations=completed, authentication_failures=failed,
                          rotation_outcome=outcome or 'validation_failed')
            return report
        finally:
            lab.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=['success', 'failed-validation', 'stale-worker'], default='success')
    args = parser.parse_args()
    print(json.dumps(demo(args.scenario), indent=2))
