"""Read-only expiry planner. Input is metadata, never secret values."""
import argparse
from datetime import datetime, timezone
import json
import re


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be a timezone-aware ISO string')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp requires a timezone')
    return parsed.astimezone(timezone.utc)


def plan(records, now):
    now = timestamp(now)
    if not isinstance(records, list):
        raise ValueError('inventory must be a list')
    result = []
    names = set()
    allowed = {'name', 'owner', 'secret_ref', 'provider_expires_at',
               'rotate_by', 'overlap_supported', 'renewal'}
    for record in records:
        if not isinstance(record, dict) or set(record) != allowed:
            raise ValueError('inventory requires exactly the metadata fields; secret values are forbidden')
        for field in ('name', 'owner'):
            if not isinstance(record[field], str) or not re.fullmatch(r'[a-zA-Z0-9_.-]{1,64}', record[field]):
                raise ValueError('name and owner must be short identifiers')
        if record['name'] in names:
            raise ValueError('duplicate integration')
        names.add(record['name'])
        if not isinstance(record['secret_ref'], str) or not re.fullmatch(r'secrets/[a-z0-9_/-]{1,100}', record['secret_ref']):
            raise ValueError('use a secret reference, never a key value')
        overlap = record['overlap_supported']
        if overlap is not None and type(overlap) is not bool:
            raise ValueError('overlap support must be true, false or null')
        if record['renewal'] not in ('manual', 'api', 'unverified'):
            raise ValueError('renewal must be manual, api or unverified')
        deadlines = []
        for field in ('provider_expires_at', 'rotate_by'):
            if record[field] is not None:
                deadlines.append((timestamp(record[field]), field))
        if not deadlines:
            status, remaining, deadline_type = 'unknown', None, None
        else:
            deadline, deadline_type = min(deadlines, key=lambda x: x[0])
            remaining = (deadline - now).total_seconds() / 86400
            status = ('overdue' if remaining <= 0 else 'urgent' if remaining <= 1
                      else 'soon' if remaining <= 7 else 'upcoming' if remaining <= 30 else 'healthy')
        automatic = overlap is True and record['renewal'] == 'api'
        result.append({'name': record['name'], 'owner': record['owner'],
                       'status': status, 'days_remaining': remaining,
                       'deadline_type': deadline_type,
                       'next_action': 'verify-provider-contract' if record['renewal'] == 'unverified' or overlap is None
                       else 'adapter-validation-required' if automatic else 'manual-renewal-required'})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory')
    parser.add_argument('--now', default=datetime.now(timezone.utc).isoformat())
    args = parser.parse_args()
    try:
        output = plan(json.loads(open(args.inventory).read()), args.now)
        print(json.dumps(output, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, 'Invalid credential metadata: ' + str(exc) + '\n')
