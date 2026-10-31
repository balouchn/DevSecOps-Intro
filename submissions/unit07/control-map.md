# Unit 07 · Control Map

## Observed behavior -> control

| Observed behaviour | Control that produced it | Layer | Depends on | Logged? | Independence verdict |
|---|---|---|---|---|---|
| E1 stayed healthy after `juice-a` stopped | `upstream juice { server juice-a:3000 ...; server juice-b:3000 ...; }` plus `proxy_next_upstream error timeout http_502 http_503;` | Availability | Docker networking, the `juice` upstream, and the remaining replica | Yes, via access log and response `X-Served-By` | Not independent: both replica paths are on the same host, same Docker network, same failure mode (network/port availability) |
| `/api/Products` and `/rest/admin/application-configuration` failed when `idp` stopped | `location /api/ { auth_request /_auth; ... }` and `location /rest/ { auth_request /_auth; ... }` | Authentication | IDP service `idp:8081/validate` and its network path | Yes, Nginx logs recorded the 500s | Not independent: both protected routes share the same auth dependency and the same operator (Nginx config) |
| E3 became slow before failing | `proxy_read_timeout 10s;` on `location = /_auth` before Task 4 | Recovery / timeout | IDP reachability and request timing | Yes, probe response times reached ~10s | Not independent: same IDP dependency and same timeout policy; a single slow or hung identity provider stalls every protected route |
| `/edge-health` stayed 200 even while protected routes failed | `location = /edge-health { access_log off; return 200 "edge ok\n"; }` | Detection / health | Only the local edge proxy | Yes, but it is intentionally a static health check | Not independent: it does not test the real upstream or IDP dependencies |
| Localhost-only exposure prevented unrelated hosts from seeing the lab traffic | `ports: - "127.0.0.1:8080:80"` in `docker-compose.yml` | Boundary | Docker host network binding and OS loopback | Not directly; the bind itself is the control | It is independent of the app logic, but not independent of the host OS and container runtime |

## Which control made recovery slower or less safe than it needed to be?

The primary control was the original `/_auth` timeout: `proxy_read_timeout 10s;`. When `idp` was paused, Nginx held each protected request open for about ten seconds before failing it. That made a hung dependency look like a slow, noisy outage rather than a fast detect-and-fail event. The faster timeout change in Task 4 reduced that stall window to 2 seconds, but it did not eliminate the underlying outage when the dependency was unavailable.

## Independence verdict

I applied the three tests:

- Vendor: the edge, IDP, and both Juice Shop replicas are all in the same Docker Compose project and same Docker network, so they are not independent vendors in a system-of-systems sense.
- Failure mode: the same host-and-network failure mode affects the upstream and auth control path at once.
- Operator: the same operator (project configuration) controls the auth logic, timeout policy, and health check behavior.

Conclusion: the relied-on controls are not independent. A single dependency failure in the shared IDP path can take down all authenticated routes at once.
