# Unit 07 · Control Map

## Observed behavior -> control

| Observed behaviour | Exact control | Layer | Depends on | Logged? | Independence verdict |
|---|---|---|---|---|---|
| E1 had 532/532 status-200 responses after Juice Shop replica A stopped | `upstream juice` lists both replicas in `nginx.conf`; `proxy_next_upstream error timeout http_502 http_503` is configured on the edge server | Availability | Docker network and remaining replica | Probe CSV and Nginx access log | Not independent: replicas share host, Docker network, and the same operator |
| IDP stop/pause caused protected route failures | `auth_request /_auth` appears in both `location /api/` and `location /rest/`; `/_auth` proxies to `http://idp:8081/validate` | Authentication | IDP availability and Docker network | Probe CSV and Nginx error/access logs | Shared dependency: one IDP failure reaches both routes |
| `/` remained 200 during IDP faults | `location / { proxy_pass http://juice; }` has no `auth_request` | Availability boundary | Juice replicas only | Probe CSV | Independent of IDP for that route, but not independent of Juice replicas |
| `/edge-health` remained 200 during IDP faults | `location = /edge-health { return 200 "edge ok\n"; }` is a static response | Detection | Edge process only | Probe CSV; endpoint intentionally has access logging disabled | Not an independent dependency check |
| Protected requests stalled near 2 seconds in the measured runs | `proxy_read_timeout 2s` under `location = /_auth` in the current Nginx configuration | Timeout recovery | IDP response time | Probe CSV and error log | Shared timeout policy controls both protected route families |
| Lab traffic is limited to the host | `ports: - "127.0.0.1:8080:80"` in `docker-compose.yml` | Boundary/safety | Docker host loopback binding | Configuration | Independent of application failure mode, but controlled by host/Docker operator |

## Controls requiring attention

- The quickest shared recovery control to reduce a hung-auth wait is the 2-second `proxy_read_timeout`, changed from 10 seconds in Task 4.
- This change improves fail-fast time but does not restore protected availability when IDP is stopped; E2b still had 108 protected-route failures out of all protected requests.
- The static `/edge-health` control is unsafe as a broad service indicator: it can remain 200 while protected routes fail.

## Independence verdict

Three tests do not support independence among the identity-protected controls:

- Vendor: edge, IDP, and replicas are separate container images but belong to the same Compose project and shared host runtime.
- Failure mode: IDP loss simultaneously crosses the same authentication control used by `/api/` and `/rest/`.
- Operator: one lab compose file, one Nginx configuration, and one Docker network operator control the affected services.

Therefore, `/api/` and `/rest/` are not independent protection paths. Public `/` and `/edge-health` also do not validate IDP availability.
