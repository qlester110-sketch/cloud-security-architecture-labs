# Portfolio Readiness Audit, 5 Oct 2026

Local audit of this repository before it is shown to recruiters. Nothing in this audit has been pushed or published. Every change sits on the local branch `portfolio-readiness-2026-10-05`.

**Status of the code:** not marked polished. The Python tools were generated with AI assistance. They stay "in progress" until Quentin has read each tool, can explain every rule, and has reviewed the open code findings below.

## How this was verified

1. Fresh `git clone` of local `main` (commit `e3bd254`) into a temporary directory.
2. Full test suite run on Python 3.14.7 (Homebrew) and Python 3.9.6 (macOS system).
3. Every command in every README extracted and run exactly as written.
4. Edge-case inputs fed to each tool to look for fail-open behavior.
5. Secret patterns and private-term list checked against the working tree and all six commits of history.
6. Read-only check of GitHub: visibility, license detection, last CI runs, live Pages site.

## Test results

```text
$ python3 -m unittest discover -s tests -v      # Python 3.14.7, readiness branch
Ran 25 tests in 0.003s
OK

$ /usr/bin/python3 -m unittest discover -s tests # Python 3.9.6
Ran 25 tests in 0.002s
OK
```

| Test module | Tests | Result |
| --- | --- | --- |
| test_oidc_trust_policy | 5 | pass |
| test_kubernetes_baseline | 3 | pass |
| test_supply_chain | 6 | pass |
| test_ai_ingestion | 5 | pass |
| test_detection_as_code | 6 | pass |
| **Total** | **25** | **25 pass, 0 fail, 0 error** |

Documented CLI commands, run from the repository root after the README changes:

| Command | Exit | Expected |
| --- | --- | --- |
| 01 generate trust policy | 0 | yes, prints policy with `<ACCOUNT_ID>` placeholder |
| 02 check secure deployment | 0 | yes, PASS |
| 02 check insecure deployment | 1 | yes, 8 findings |
| 03 gate secure release | 0 | yes, PASS |
| 03 gate insecure release | 1 | yes, 10 findings |
| 04 ingest safe record | 0 | yes, allow |
| 04 ingest injection record | 1 | yes, quarantine |
| 05 detect events | 1 | yes, 3 alerts from 4 events |
| 5 per-project unittest commands | 0 | yes |

GitHub Actions on the published `main` (read-only check): last "Security tests" and "Deploy portfolio site" runs both succeeded on 21 Sep 2026. Live site returns HTTP 200.

## Audit by project

Key: ✅ meets the bar · 🟡 partly · ❌ missing

| Criterion | 01 Landing zone | 02 Kubernetes | 03 Supply chain | 04 AI ingestion | 05 Detection |
| --- | --- | --- | --- | --- | --- |
| Clean checkout runs | ✅ | ✅ | ✅ | ✅ | ✅ |
| Setup steps | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tests | ✅ 5 | 🟡 3, thin | 🟡 3, thin | ✅ 5 | ✅ 6 |
| Safe examples | ✅ placeholder account | ✅ | ✅ placeholder digests | ✅ synthetic | ✅ AWS doc account |
| Architecture explained | ✅ diagram, ADR, threat model | ✅ diagram added | ✅ diagram added | ✅ diagram, principles | 🟡 runbook, no diagram |
| Limitations stated | ✅ added | ✅ added | ✅ added | ✅ added | ✅ added |
| Matches its title | 🟡 AWS only, no Terraform | ✅ | 🟡 evaluates evidence, does not produce it | ✅ ingestion half only | ✅ |
| Recruiter readability | 🟡 | ✅ live demo | 🟡 | ✅ | 🟡 |

Repository-wide:

| Criterion | Result |
| --- | --- |
| License | ❌ before, ✅ after. GitHub detected the license as "Other" because `LICENSE` held only the short Apache notice. Replaced with the full Apache 2.0 text from GitHub's license API, copyright line filled in |
| Secret scan, working tree and full history | ✅ No AWS keys, private keys, GitHub tokens, Slack tokens, API keys or 12-digit account IDs other than the AWS documentation account `111122223333`. No dedicated scanner (gitleaks, trufflehog) is installed, so this was a pattern scan |
| Private and employer terms | ✅ Zero hits for the private banned-terms list across HEAD and all history. Zero hits for business, client or pricing terms |
| Dependencies | ✅ Python standard library only. Nothing to install, nothing to audit |
| CI | 🟡 Runs on every push and pull request. Third-party actions are pinned by version tag, not commit SHA, which `SECURITY.md` says should happen before a project is called complete |

## Recommended for LinkedIn Featured

1. **Kubernetes security baseline (02).** It is the only project with something a recruiter can click and use in ten seconds: the browser checker on the live site. It also targets the Kubernetes gap that kept appearing in target-role analysis. Feature the live site URL, not the folder.
2. **AI ingestion guardrail (04).** The strongest written explanation in the repository: why ingestion is a trust boundary, ten principles, a clear decision table. AI security is the least common skill among other applicants. It is also easy to explain in an interview because the rules are simple and deterministic.

**Runner-up: landing zone (01).** It has the best architecture documents (ADR and threat model) and sits closest to hands-on experience with keyless pipelines. It should move into Featured once Terraform exists, because today the title promises more than the 53-line generator delivers.

Do not feature 05 yet. Project 03's original fail-open path, malformed-count crash, source-repository validation, and browser `innerHTML` issue were repaired locally after this audit and are now covered by 25 passing tests. It remains behind projects 02 and 04 for recruiter readability.

## Code findings

These were found by probing with edge-case inputs. They are documented in each README's limitations section. The code was left unchanged so Quentin can review and fix them himself and be able to explain the fix.

| # | Project | Finding | Suggested fix |
| --- | --- | --- | --- |
| 4 | 02 | `privileged: true`, `hostNetwork`, `hostPath` and `initContainers` are not checked. | Add rules K8S-010 onward, mirror them in `docs/app.js`. |
| 5 | 02 | `registry.local:5000/app` (no tag) passes K8S-005. | Parse the tag after the last `/`. |
| 6 | 05 | Root console login produces no alert. Failed logins are labelled "succeeded". | Alert on any root activity. Check `responseElements.ConsoleLogin`. |
| 7 | 05 | SSH exposure missed for port ranges and IPv6 `::/0`. | Check `fromPort <= 22 <= toPort` and `cidrIpv6`. |
| 8 | 04 | Single word "reveal" quarantines benign text. Spaced-out text evades. AWS keys not redacted. | Tighten patterns, add AKIA pattern, measure false positives. |

Fixed after the initial audit:

- Project 03 now fails closed when vulnerability evidence is missing, negative, boolean, or non-integer.
- SC-008 now requires the approved portfolio repository instead of accepting any GitHub URL.
- Three new supply-chain tests cover missing evidence, malformed counts, and an unapproved repository.
- The browser checker now creates result nodes with `textContent`; it no longer inserts findings through `innerHTML`.

## Changes made on the local branch

- `LICENSE`: full Apache 2.0 text so GitHub detects it correctly.
- `README.md`: one-paragraph summary, live demo link, "Start here" pointing at 02 and 04, quick start with expected result, honest per-project table of what runs today versus what is planned, repository layout, exit-code convention.
- All five project READMEs: plain status lines that separate working from planned, `python3` run steps from the repository root, sample output captured from the clean clone, and a known-limitations section. Diagrams added to 02 and 03.
- Corrected claims that overstated the code: 02 said "admission controls complete" and "immutable image references", but it is an offline checker that requires a tag, not a digest. 01 now says a fork is blocked by the trust policy, and that keeping other branches out depends on GitHub environment protection.
- `docs/index.html`: "immutable images" changed to "pinned image tags". Note that this file deploys the live site the next time `main` is pushed.
- This file.

## Decisions for Quentin, all need your go in-session

1. **Merge and push** the branch `portfolio-readiness-2026-10-05` to `main`. A push redeploys the live site.
2. **This file's name** contains the coach's name, which is on the private banned-terms list, so the push guard would flag it and it would be public if pushed. Rename it (for example `PORTFOLIO-READINESS.md`) or keep it out of the push.
3. **Repository settings:** add the live site as the repository homepage and add topics (cloud-security, kubernetes, devsecops, ai-security, detection-engineering). Both fields are empty today.
4. **Commit email:** all six public commits show a personal Gmail address. Consider switching this repository to the GitHub noreply address for future commits.
5. **Code fixes 1 to 9** above, ideally written by you, starting with the fail-open in 03.
6. **Pin GitHub Actions by commit SHA**, which the repository's own `SECURITY.md` asks for.
