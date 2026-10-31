# Unit 07 · Observed Timeline

## Evidence used

- `results/probe-baseline.csv`
- `results/probe-E1.csv`
- `results/probe-E2.csv`
- `results/probe-E3.csv`
- `results/probe-E2b.csv`
- `results/docker-events.csv`
- `results/access.log`
- `results/error.log`

All times are UTC.

## Timestamped events

| Time (UTC) | What happened | Source |
|---|---|---|
| 2026-10-31T22:09:20Z | Baseline probe starts; `/edge-health`, `/`, `/api/Products`, and `/rest/admin/application-configuration` all return 200 | probe-baseline.csv |
| 2026-10-31T22:13:31Z | `u07-idp-1` is killed/stopped/dies during the earlier IDP stop experiment | docker-events.csv |
| 2026-10-31T22:14:32Z | `u07-idp-1` restarts | docker-events.csv |
| 2026-10-31T22:15:36Z | E2 begins; `/` stays healthy while `/api/Products` and `/rest/admin/application-configuration` start failing | probe-E2.csv |
| 2026-10-31T22:18:05Z | E2 window ends; protected routes remain impacted while `/edge-health` stays 200 | probe-E2.csv |
| 2026-10-31T22:18:19Z | E3 begins; `idp` is paused, protected routes develop timeouts and 500s | probe-E3.csv |
| 2026-10-31T22:20:48Z | E3 ends; `idp` is unpaused; requests recover | probe-E3.csv |
| 2026-10-31T22:21:21Z | E2b begins after the timeout reduction change; protected routes still fail when `idp` is stopped | probe-E2b.csv |

## What alerted, what did not

- `curl http://127.0.0.1:8080/edge-health` stayed at 200 in every run.
- `/` stayed at 200 in all three fault experiments, as expected for the public route.
- E1 (`docker compose stop juice-a`) caused no 500s; the upstream failover kept the site healthy. The only observed difference was that the `X-Served-By` header moved to the remaining replica.
- E2 (`docker compose stop idp`) caused protected requests to fail with 500s and `served_by` was `-` on many `/api` and `/rest` rows.
- E3 (`docker compose pause idp`) caused a slower failure pattern: the same protected endpoints returned 500s and saw request times near or above 10 seconds, which matches the `proxy_read_timeout 10s` behavior in the original `nginx.conf`.
- The edge health endpoint did not indicate a dependency failure; it only reported that nginx itself was alive.

## Browser observation

The browser was kept open during E2 and E3. The manual browser screenshot step could not be collected automatically in this environment, so the smallest remaining manual step is:

1. Open `http://127.0.0.1:8080` in your browser while E2 or E3 is running.
2. Save the visible page as `submissions/unit07/results/E2-browser.png` and `submissions/unit07/results/E3-browser.png`.

The public home page remained visible in both experiments, while the authenticated products/admin routes were the ones that failed.

## Log evidence

- `results/access.log` recorded the failing probe requests to `/api/Products` and `/rest/admin/application-configuration`.
- `results/error.log` was empty in the captured runs, meaning the 500 responses were handled by Nginx and the application responses, not by a fatal edge error.
- No out-of-project Docker container changed state during the lab runs.
