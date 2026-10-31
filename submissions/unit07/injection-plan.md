# Unit 07 · Injection Plan

## Student and environment

- Student name: **Noorulain Balouch**
- Environment: **Docker Desktop on Windows (WSL 2)**
- Scope: Only the Docker Compose project `u07`; the edge publishes only `127.0.0.1:8080`.

## Baseline steady state

**Measured baseline, collected 2026-10-28 while all four services were healthy:**

```text
rows=100; 25 samples per endpoint
/                         25/25 200; worst 0.118793 s; served by .11 13, .12 12
/api/Products             25/25 200; worst 0.175213 s; served by .12 13, .11 12
/rest/admin/application-configuration 25/25 200; worst 0.060204 s; served by .11 13, .12 12
/edge-health              25/25 200; worst 0.011417 s
```

The baseline was collected with:

```bash
cd labs/unit07
./probe.sh 30 > ../../submissions/unit07/results/probe-baseline.csv
```

Normal upstream traffic alternated between `172.28.7.11:3000` and `172.28.7.12:3000` on the three application endpoints. `/edge-health` remained a local Nginx 200 and reported no upstream.

## Configuration basis

- `/api/` and `/rest/` use `auth_request /_auth`; thus both depend on `idp:8081/validate` ([nginx.conf](../../labs/unit07/edge/nginx.conf)).
- `/_auth` has a 2-second connect timeout and 10-second read timeout.
- Public `/` and `/edge-health` do not use `auth_request`.
- `proxy_next_upstream error timeout http_502 http_503` applies to the Juice Shop upstream.
- `/edge-health` always returns 200 locally and does not test the replicas or IDP.
- Only `127.0.0.1:8080` is published by the Compose project.

## E1 · Stop one Juice Shop replica

**Hypothesis:** Stopping `juice-a` should leave the public front end and authenticated API routes available through `juice-b`, because the `juice` upstream contains both replicas and Nginx retries `error timeout http_502 http_503`. Requests already in flight may briefly fail or incur a retry, and `X-Served-By` should show only or eventually return to `172.28.7.12` for the stopped replica interval. Measurement is required to confirm exact timing and whether the retry is observable by the probe.

**Predicted affected endpoints:** Possibly `/`, `/api/Products`, and `/rest/admin/application-configuration` during retries; `/edge-health` should remain 200 because it is static.

**Detection expectation:** Probe status and latency changes; container `stop` and `start` events; Nginx logs. No external alert is assumed unless monitoring is separately configured.

**Abort condition:** Stop immediately if any container outside project `u07` changes state, the host becomes unresponsive, traffic appears outside `127.0.0.1`, or local scope cannot be restored with the commands below.

**Fault:** `docker compose stop juice-a`

**Restore:** `docker compose start juice-a`

## E2 · Stop the shared identity provider

**Hypothesis:** Stopping `idp` should affect `/api/Products` and `/rest/admin/application-configuration`, because every request to those routes passes through `auth_request /_auth`. Expected denial or failure depends on the version of Nginx auth_request behavior; actual status must be measured rather than assumed. `/` and `/edge-health` should remain available because they do not depend on IDP auth.

**Predicted affected endpoints:** `/api/Products` and `/rest/admin/application-configuration`; probably `/` traffic remains served, while `/edge-health` remains 200.

**Detection expectation:** The probe should identify when protected endpoint success drops or latency changes; container `stop/start` events and edge logs should record the failure after it reaches the edge. Actual alert behavior and browser behavior require measurement.

**Abort condition:** Same project/host/loopback scope conditions, plus inability to restore IDP immediately.

**Fault:** `docker compose stop idp`

**Restore:** `docker compose start idp`

## E3 · Pause the shared identity provider

**Hypothesis:** Pausing `idp` should make its process appear running but unable to schedule, so protected `/api/` and `/rest/` requests should wait until the auth subrequest read/connect timeout or until an upstream error is returned. The exact status and latency depend on the measured environment. Public `/` and `/edge-health` should remain available.

**Predicted affected endpoints:** `/api/Products` and `/rest/admin/application-configuration`; `/` and `/edge-health` should not be paused directly.

**Detection expectation:** Protected requests should develop timeout-dependent latency near or below the configured 10-second read timeout, then return  failure when the fault window ends; Docker `pause/unpause` events should be present. Exact status codes and recovery duration require measurement.

**Abort condition:** Same project/host/loopback scope conditions, plus inability to unpause IDP immediately.

**Fault:** `docker compose pause idp`

**Restore:** `docker compose unpause idp`

## Experiment procedure and safety

1. Run each experiment separately and in E1, E2, E3 order.
2. Run the 150-second probe as specified: 30 seconds steady, 60 seconds fault, 60 seconds recovery.
3. Restore the target service after each experiment before starting the next.
4. Record container events for the complete experiment window. Do not collect traffic or data outside localhost.
5. Keep the browser on `http://127.0.0.1:8080` for E2 and E3 and save the required screenshots under `submissions/unit07/results/`.

## Global restoration

```bash
cd labs/unit07
docker compose start
# if IDP was paused:
docker compose unpause idp
# if the experiment must be fully stopped:
docker compose down
```

## Safety statement

This experiment runs only in the local Docker Compose project `u07`, with all application exposure bound to `127.0.0.1` and no cloud resources. No unrelated Docker container will be stopped, paused, started, or removed. If any out-of-project container changes state, the host becomes unresponsive, traffic is observed outside loopback, or restoration fails, work will stop and the global restoration commands will be run immediately.
