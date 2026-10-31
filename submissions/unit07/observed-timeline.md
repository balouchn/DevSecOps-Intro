# Unit 07 · Observed Timeline

Evidence used: `results/probe-baseline.csv`, `results/probe-E1.csv`, `results/probe-E2.csv`, `results/probe-E3.csv`, `results/probe-E2b.csv`, `results/docker-events.csv`, `results/access.log`, and `results/error.log`. All CSV timestamps are UTC.

## Timestamped measurements

| Observation window (UTC) | Measurement | Source |
|---|---|---|
| 2026-10-28 22:23:36–22:24:05 | Baseline: each of four endpoints returned 200 for all 25 requests. | `probe-baseline.csv` |
| 2026-10-31 22:09:20–22:11:49 | E1: all 532 requests returned 200; no protected-route failures occurred. | `probe-E1.csv` |
| 2026-10-31 22:38:29–22:40:58 | E2 rerun: `/api/Products` had 52 failures and admin had 53 failures with status 500; public `/` and `/edge-health` remained 200. | `probe-E2.csv` |
| 2026-10-31 22:41:13–22:43:42 | E3 rerun: `/api/Products` had 50 failures and admin had 50 failures with status 500; public endpoints remained 200. | `probe-E3.csv` |
| 2026-10-31 22:21:21–22:23:50 | E2b: `/api/Products` and admin each had 54 failures with status 500; public endpoints remained 200. | `probe-E2b.csv` |

## Alerting and non-alerting signals

- Protected-route failures were visible in the probe CSVs immediately: 52–54 of the 133-sample protected-route sequence returned 500 in the stop/Task-4 runs.
- `/edge-health` remained 200 for every row in the baseline and all fault CSVs. It is a static Nginx response and did not detect the IDP outage.
- `/` remained 200 in E2 and E3, so a public-page or home-page monitor would not have revealed the protected API outage.
- Nginx recorded auth upstream timeouts and `auth request unexpected status: 504`, while the probes recorded the final edge status as 500. This is consistent with Nginx conversion to an unexpected-status 500 in the saved data; reports do not treat the CSV and log status values as interchangeable.
- No browser screenshots could be created: browser automation was unavailable in the execution environment. The files `E2-browser.png` and `E3-browser.png` are therefore not claimed as evidence.

## E2/E3 latency

The worst measured protected-route time in the renewed E2 file was 2.011848 seconds. The renewed E3 file had a worst protected-route time of 2.011459 seconds. In the current edge configuration the `/ _auth` read timeout is 2 seconds, so these maximums are consistent with the configured timeout rather than the unsupported prior claim of 10 seconds.

## Logs and Docker scope

The copied Nginx logs contain protected-route auth timeout/504 messages. The Docker events file records the in-scope project containers, but the committed event format was damaged during collection and must not be used to infer exact stop/start seconds that it does not contain. No container outside the `u07` Compose project was stopped, paused, or started by the experiments; restoration was performed with the compose service commands.
