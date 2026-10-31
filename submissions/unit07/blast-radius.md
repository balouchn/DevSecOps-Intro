# Unit 07 · Blast Radius

## Predicted vs measured

### Prediction before experiments

- E1: one replica loss should be survivable because the upstream has two servers and the edge uses `proxy_next_upstream` to retry failed upstreams.
- E2: stopping `idp` should affect every `/api/` and `/rest/` request because those routes require `auth_request /_auth` before they reach a replica.
- E3: pausing `idp` should look slower than stopping it, because Nginx may keep waiting on the auth request until the `proxy_read_timeout` expires.

### Measured result

- E1 stayed healthy for all endpoints: `532/532` requests were 200.
- E2: `/api/Products` and `/rest/admin/application-configuration` failed with `500` while `/` and `/edge-health` stayed 200. The protected routes lost 108 of 532 requests.
- E3: same protected endpoints failed again, but the failure pattern was slower, with worst latency near `10s` because the old timeout was `proxy_read_timeout 10s;`.
- E2b: after the timeout change to 2s, the protected routes still failed when `idp` was stopped. The change reduced time-to-fail under a hung provider, but it did not restore service when the identity provider was unavailable.

## Finding: the gap between prediction and measurement

The main gap was that the edge health endpoint told a lie. `/edge-health` always returned 200 even when the shared identity provider was down. That meant a monitor polling only `/edge-health` would not detect the real outage. The actual blast radius was limited to authenticated routes; the public front page stayed alive, but every identity-guarded route failed as soon as the IDP stopped responding.

## Radius along role, location, and time

- Role: all users who needed `/api/` or `/rest/` routes were affected; unauthenticated public read access to `/` continued.
- Location: the effect was confined to the local lab host because all Docker ports were bound to `127.0.0.1` and only the lab project was affected.
- Time: the failure window was approximately the 60-second fault period in each experiment, with recovery occurring after `docker compose start idp` or `docker compose unpause idp`.

## What a larger system would lose

If this system were scaled beyond a single lab host, an IDP outage would deny authenticated reads and writes for everyone who depends on tokens or introspection, while the public front end stayed online. The larger risk is not a total site outage; it is a partial outage that looks like the app is alive even though the protected API layer is dead.

## Task 4 decision and trade-off

I changed the identity subrequest timeout from `10s` to `2s` in `edge/nginx.conf`.

Why:
- The original timeout let a hung IDP stall authenticated requests for up to ten seconds.
- A shorter timeout is a safer fail-fast policy for a shared identity dependency because it reduces the time a user session is left waiting on a dependency that is already dead.

Trade-off:
- Fail closed: protected routes fail faster instead of waiting a long time for a hung identity provider.
- Impact: some legitimate slow-auth requests may fail sooner than before, but the system is no longer silently hanging on a dead dependency.

E2b measurement:
- Measured after the timeout change, `probe-E2b.csv` still showed 108 protected-route failures when `idp` was stopped.
- The change did not restore availability during a dead IDP. It only reduced delay before a hung provider failed.

## Residual risk

The remaining risk is the shared identity provider outage itself: if `idp` is down or paused, the protected routes fail even though `/` and `/edge-health` remain accessible. The edge health check is not a real dependency test. For production, the system would need a better dependency health check and likely a fallback or degraded mode for public reads.
