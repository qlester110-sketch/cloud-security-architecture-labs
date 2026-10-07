# Portfolio Readiness Audit, 5 Oct 2026

Local audit of this repository before its October 2026 portfolio update.

**Status of the code:** not marked polished. The Python tools were generated with AI assistance. They stay "in progress" until Quentin has read each tool, can explain every rule, and has reviewed the open code findings below.

**Follow-up on 7 Oct 2026:** findings 4 through 8 below were repaired and covered by regression tests. A repository-and-environment-scoped GitHub-to-AWS OIDC Terraform reference flow was also added. The suite now contains 41 passing tests. The projects remain labelled in progress because their stated production limitations still apply.

## How this was verified

1. Fresh clone verification and repeated runs from the repository root.
2. Full test suite run with Python 3.14.
3. Every command in every README extracted and run exactly as written.
4. Edge-case inputs fed to each tool to look for fail-open behavior.
5. Secret patterns and private-term list checked against the working tree and all six commits of history.
6. Read-only check of GitHub: visibility, license detection, last CI runs, live Pages site.

## Test results

```text
$ python3 -m unittest discover -s tests -v
Ran 41 tests
OK
```

| Test module | Tests | Result |
| --- | --- | --- |
| test_oidc_trust_policy | 5 | pass |
| test_aws_oidc_terraform | 7 | pass |
| test_kubernetes_baseline | 6 | pass |
| test_supply_chain | 6 | pass |
| test_ai_ingestion | 8 | pass |
| test_detection_as_code | 9 | pass |
| **Total** | **41** | **41 pass, 0 fail, 0 error** |

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

Before publication, the previously deployed site returned HTTP 200 and its last published workflow run was successful. The updated workflow and site require post-push verification.

## Audit by project

Key: ✅ meets the bar · 🟡 partly · ❌ missing

| Criterion | 01 Landing zone | 02 Kubernetes | 03 Supply chain | 04 AI ingestion | 05 Detection |
| --- | --- | --- | --- | --- | --- |
| Clean checkout runs | ✅ | ✅ | ✅ | ✅ | ✅ |
| Setup steps | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tests | ✅ 12 | ✅ 6 | ✅ 6 | ✅ 8 | ✅ 9 |
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
| CI | 🟡 Runs on every push and pull request. Third-party actions are pinned by version tag, not commit SHA, which `SECURITY.md` identifies as a remaining hardening task |

## Recommended for LinkedIn Featured

1. **Kubernetes security baseline (02).** It is the only project with something a recruiter can click and use in ten seconds: the browser checker on the live site. It also targets the Kubernetes gap that kept appearing in target-role analysis. Feature the live site URL, not the folder.
2. **AI ingestion guardrail (04).** The strongest written explanation in the repository: why ingestion is a trust boundary, ten principles, a clear decision table. AI security is the least common skill among other applicants. It is also easy to explain in an interview because the rules are simple and deterministic.

**Runner-up: landing zone (01).** It has the best architecture documents (ADR and threat model) and sits closest to hands-on experience with keyless pipelines. It should move into Featured once Terraform exists, because today the title promises more than the 53-line generator delivers.

Do not feature 05 yet. Project 03's original fail-open path, malformed-count crash, source-repository validation, and browser `innerHTML` issue were repaired after the initial audit and are now covered by regression tests. It remains behind projects 02 and 04 for recruiter readability.

## Code findings

These were found by probing with edge-case inputs. They were documented in each README and subsequently repaired with regression coverage.

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
- Project 02 now checks init containers, privileged mode, host namespaces and host-path volumes, and correctly distinguishes a registry port from an image tag. The browser demo mirrors the new rules.
- Project 04 no longer quarantines the standalone word `reveal`, catches a small set of spaced-out injection phrases, and redacts AWS access-key IDs.
- Project 05 now alerts on root console activity, distinguishes failed console authentication, and detects public SSH exposure through port ranges and IPv6.

## Changes made on the local branch

- `LICENSE`: full Apache 2.0 text so GitHub detects it correctly.
- `README.md`: one-paragraph summary, live demo link, "Start here" pointing at 02 and 04, quick start with expected result, honest per-project table of what runs today versus what is planned, repository layout, exit-code convention.
- All five project READMEs: plain status lines that separate working from planned, `python3` run steps from the repository root, sample output captured from the clean clone, and a known-limitations section. Diagrams added to 02 and 03.
- Corrected claims that overstated the code: 02 said "admission controls complete" and "immutable image references", but it is an offline checker that requires a tag, not a digest. 01 now says a fork is blocked by the trust policy, and that keeping other branches out depends on GitHub environment protection.
- `docs/index.html`: "immutable images" changed to "pinned image tags". Note that this file deploys the live site the next time `main` is pushed.
- This file.

## Remaining hardening work

- Pin third-party GitHub Actions to reviewed commit SHAs.
- Exercise the Terraform reference module with `terraform validate` before describing it as runtime-validated.
- Replace synthetic release evidence with real SBOM generation and signature verification.
- Add safe cloud attack simulation and time-to-detect measurement to the detection lab.
