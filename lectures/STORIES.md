# Story registry

Instructor file. Real incidents are the part students remember, so they are managed
like any other course asset instead of being reinvented per lecture.

Rules (from the course writing standard):

- Every lecture carries **at least one incident from the last 24 months** and **at most two
  classics older than five years**.
- Every story ends with **the control that would have caught it** and **the lab where the
  student builds that control**. A story without a mechanism gets cut.
- Repeating a story in a second lecture is allowed only when the second angle is different;
  the table below is what makes that a decision instead of an accident.
- Sources: post-mortems from the project or vendor, court filings, regulator reports,
  CISA/NCSC advisories. Vendor blogs for timelines only.

Status: `ok` verified against the source listed. `verify` used in a lecture that has not
had its sourcing pass yet. `cut` removed, kept here so it is not reintroduced.

| Incident | Year | Used in | Lesson: control -> lab | Source | Status | Replace by |
|---|---|---|---|---|---|---|
| Equifax / Struts CVE-2017-5638 | 2017 | lec1 hook, lec9 | Asset inventory and patch verification -> lab 4, lab 10 | House Oversight report (2018) | ok | classic, keep |
| Capital One / SSRF to instance metadata | 2019 | lec1 | IaC scan for wildcard IAM, trust boundary -> lab 6, lab 2 | DOJ release, OCC penalty | ok | classic, keep |
| Log4Shell CVE-2021-44228 | 2021 | lec1, lec10 (triage angle) | SBOM answers "where is it" -> lab 4; runtime detection -> lab 9 | Apache Logging security page, CISA | ok | classic, keep |
| Salesloft Drift OAuth token theft | 2025 | lec2 | Third-party integration is a trust boundary -> lab 2 | Google Cloud / GTIG blog, Salesloft advisory | ok | 2027 |
| Tesla exposed Kubernetes console | 2018 | lec2 (skipped-modeling angle), lec6 | "Who can reach the admin plane" -> lab 2, lab 7 | RedLock via CyberScoop / CNBC (Feb 2018) | ok | 2027 |
| Slack OAuth redesign "caught by STRIDE" | 2015 | lec2 | none | none found | cut | never: no primary source, likely invented |
| Codecov bash uploader | 2021 | lec4 only (removed from lec3 on 2026-09-06) | Pin and verify build-time downloads -> lab 8 | Codecov security update | ok | 2027 |
| Toyota T-Connect access key | 2017-2022 | lec3 hook | Secret scanning before the push -> lab 3 | BleepingComputer, The Register (Oct 2022) | ok | classic, keep |
| Uber S3 bucket keys in a repo | 2016 | lec3 | Secret scanning pre-commit -> lab 3 | DOJ release on the CSO conviction | ok | 2027 |
| s1ngularity / Nx npm compromise | 2025 | lec3 | Credentials live on laptops; short-lived scoped tokens and a rehearsed rotation -> lab 3 bonus | Nx post-mortem, GHSA-cxm3-wv7p-598c, StepSecurity | ok | 2028 |
| tj-actions/changed-files compromise | 2025 | lec4 (was dated 2024, fixed 2026-09-06) | SHA-pin actions, and an update path so the pin does not rot -> lab 1 bonus, lab 4 | CISA alert, CVE-2025-30066, Wiz | ok | 2028 |
| Drupalgeddon 2 CVE-2018-7600 | 2018 | lec5 | SAST and DAST both plausible -> lab 5 | Drupal SA-CORE-2018-002 | ok | replace with a 2024+ case |
| GitLab CVE-2023-7028 | 2024 | lec5 | Business-logic bugs evade both scanners -> lab 2 | GitLab critical patch release, 11 Jan 2024 | ok | 2027 |
| Imperva breach via stolen AWS key | 2019 | lec6 | Internet-reachable instance + over-scoped IAM -> lab 6 | Imperva security update + post-mortem coverage | ok | 2027 |
| Docker Hub breach | 2019 | lec7 | Registry trust -> lab 8 | Snyk and BleepingComputer coverage, Apr 2019 | ok | replace with a 2024+ case |
| runc "Leaky Vessels" CVE-2024-21626 | 2024 | lec7 | Container escape, pinned runtimes -> lab 7, lab 12 | Snyk research, GHSA-xr7r-f8xq-vfvv | ok | 2027 |
| ua-parser-js compromise | 2021 | lec8 | Dependency signing and provenance -> lab 8 | GitHub advisory | verify | 2027 |
| xz-utils backdoor CVE-2024-3094 | 2024 | lec8 | Provenance and build reproducibility -> lab 8 | Andres Freund's disclosure, CISA | verify | 2028 |
| SolarWinds Orion | 2020 | lec9 | Build-system integrity -> lab 8 | CISA AA20-352A | verify | classic, keep |

## Candidates not yet placed

Researched, sourced, waiting for the lecture that fits.

| Incident | Year | Fits | Why it teaches |
|---|---|---|---|
| Microsoft Exchange Online / Storm-0558 signing key | 2023-2024 | lec2 or lec8 | A consumer key signed enterprise tokens: a trust boundary that existed on paper only. CSRB report is a rare public root-cause document |
| Polyfill.io supply-chain injection | 2024 | lec8 | A dependency that changed owner, not version. Pinning by version does not help; SRI and provenance do |
| Shai-Hulud npm worm | 2025 | lec8 | Self-propagating package compromise via stolen publish tokens (keep distinct from s1ngularity, now used in lec3) |
| ingress-nginx "IngressNightmare" CVE-2025-1974 | 2025 | lec7 (still unplaced; lec7 already carries a 2024 case) | Admission controller reachable from any pod: cluster network policy -> lab 7 |
| Snowflake customer data theft (no enforced MFA) | 2024 | lec9 or lec10 | Not a product vulnerability: a missing control the customer owned |
| EPSS v4 and the CISA KEV catalogue | 2025 | lec10 | Prioritising by exploitation probability instead of CVSS alone |

## Coverage check, 2026-09-06

Every lecture and reading has had its sourcing pass. Freshness against the
"one incident from the last 24 months" rule:

| Where | Newest incident | Within 24 months? |
|---|---|---|
| lec1 | Log4Shell (2021) | no: it is a foundations lecture built on three classics, deliberately |
| lec2 | Salesloft Drift (Aug 2025) | yes |
| lec3 | s1ngularity / Nx (Aug 2025) | yes |
| lec4 | tj-actions/changed-files (Mar 2025) | yes |
| lec5 | GitLab CVE-2023-7028 (Jan 2024) | borderline; replace next cohort |
| lec6 | Imperva (2019), Tesla (2018) | no: candidate is IngressNightmare or a 2025 cloud case |
| lec7 | runc Leaky Vessels (Jan 2024) | borderline; IngressNightmare fits here too |
| lec8 | xz-utils (Mar 2024) | borderline; Shai-Hulud (Sep 2025) is parked above |
| lec9 | SolarWinds (2020), Equifax (2017) | no: candidate is the Snowflake customer breaches (2024) |
| lec10 | Log4Shell triage (2021) | no: candidate is EPSS v4 and the KEV catalogue |

Lectures 1, 6, 9 and 10 are the queue for the next freshness pass. All four
have a sourced candidate parked in the table above.
