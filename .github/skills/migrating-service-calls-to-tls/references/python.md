# Python

Contents: producer · consumer · files and local · never do this · tests

The gate's E12 reads Spring Boot configuration only. For this stack E12 reports `not run: stack not read (<stack>)`, so the overall result is at best `not proven` until a person or the judge checks these settings.

Written for Python 3.9 and later with the standard `ssl` module, which every server and client library below builds on. Record the Python version and the web server (uvicorn, gunicorn, hypercorn, the standard library) first.

## Producer

Stage settings come from the environment. Suggested names, used the same way on every stack page: `TLS_CLIENT_AUTH` (`want` stages 2-4, `need` from stage 5), `TLS_LEGACY_HTTP_ENABLED` (`true` stages 2-5, `false` stage 6), `TLS_ALLOWLIST` (file path), `TLS_ALLOWLIST_ENFORCE` (`false` stages 2-3, `true` from stage 4).

```python
import os, ssl
tls_dir, key_dir = os.environ["TLS_DIR"], os.environ["TLS_KEY_DIR"]   # no defaults: fail at start-up
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.load_cert_chain(f"{tls_dir}/tls.crt", f"{key_dir}/tls.key")
ctx.load_verify_locations(cafile=f"{tls_dir}/consumers-ca.crt")   # this producer's consumer CA only
ctx.verify_mode = ssl.CERT_REQUIRED if os.environ.get("TLS_CLIENT_AUTH") == "need" else ssl.CERT_OPTIONAL
```

- **Servers.** uvicorn takes `--ssl-certfile`, `--ssl-keyfile`, `--ssl-ca-certs` and `--ssl-cert-reqs` (1 = optional, 2 = required); gunicorn takes `--certfile`, `--keyfile`, `--ca-certs` and `--cert-reqs`. Setting a minimum protocol version differs per server and version: check the version you use, and confirm with a probe that TLS 1.0 and 1.1 are refused.
- **Allowlist and access line.** The middleware needs the client certificate's CN. The standard library gives it (`conn.getpeercert()["subject"]`). Whether uvicorn, gunicorn or hypercorn pass the client certificate to the application differs per server and version: check the version you use. If the application cannot see it, stop and ask: the allowlist and the access line cannot be written there.
- The middleware: checks the CN against the allowlist file (re-read when it changes; an unreadable file allows nobody); writes the access line from [producer.md](producer.md), `probe=<id>` from the `X-TLS-Migration-Probe` header only when it matches `[A-Za-z0-9]{1,8}`, else `-`; answers 403 for an unlisted CN when enforcing.
- **Plain HTTP (stages 2-5):** a second listener without TLS, started only when `TLS_LEGACY_HTTP_ENABLED` is `true`; at stage 6 written out as `false`.
- **Health:** a separate plain listener on the management port, bound to the node network.
- **Renewal:** restart after each renewal, unless the server documents a reload; say which in the report.
- Tests: listed consumer served; unlisted gets 403; log-only mode serves; a removed line cuts the consumer off; a missing allowlist file allows nobody.

## Consumer

```python
ctx = ssl.create_default_context(cafile=f"{tls_dir}/ca-bundle.pem")   # with cafile, only that CA is trusted
ctx.minimum_version = ssl.TLSVersion.TLSv1_2
ctx.load_cert_chain(f"{tls_dir}/client.crt", f"{key_dir}/client.key")
base_url = os.environ.get("INVENTORY_BASE_URL", "")
if not base_url.startswith("https://"):
    raise RuntimeError("INVENTORY_BASE_URL must be set to an https:// URL")
```

- requests: `session.cert = (crt, key)` and `session.verify = "<path to ca-bundle.pem>"` (a path, never a boolean).
- httpx: `httpx.Client(verify=ctx)`, the context above. Recent httpx versions deprecate the `cert=` argument; the context works in all current ones.
- aiohttp: `session.get(url, ssl=ctx)`. Standard library: `urllib.request.urlopen(url, context=ctx)` or `http.client.HTTPSConnection(host, context=ctx)`.
- `create_default_context` turns host name checking on. Leave it on.
- A client reads its certificate once: restart after a renewal.
- Tests: the client is built from these files; a blank or `http://` address is refused; a server certificate for another name is refused.

## Files and local

- Paths come from the environment (`TLS_DIR`, `TLS_KEY_DIR`). Keys never live in the repository and are never committed.
- Local: certificates from `tls-migration/local/certs/` (`<producer>-server.crt`, `<producer>-consumers-ca.crt`, `server-ca.crt` as the consumer's `ca-bundle.pem`, `<producer>-<consumer>.crt`); keys `$TLS_PRIVATE_DIR/local/<producer>/server.key` and `$TLS_PRIVATE_DIR/local/<producer>/<consumer>/client.key`. Put these paths only in local-only files (`.env.local`, `docker-compose.local.yml`): E10 fails `local-dev-` references anywhere else.
- A call that must stay on plain HTTP gets exactly `# TODO: HTTPS not supported - requires infrastructure update` beside it ([analyse-and-plan.md](analyse-and-plan.md)).

## Never do this

None of these may appear, not even in tests. The gate's scanner looks for most of them; a person or the judge checks the rest:

- `verify=False`, `ssl=False`, `verify_ssl=False`;
- `ssl.CERT_NONE`, `check_hostname = False`, `ssl._create_unverified_context()`;
- `PYTHONHTTPSVERIFY=0` in code, scripts, Dockerfiles or deploy files;
- protocol constants for TLS 1.0 or 1.1, or `minimum_version` below `TLSv1_2`;
- silencing the warning instead of fixing the cause (`urllib3.disable_warnings`).

## Tests and JUnit XML

E1 reads JUnit-style XML only. Write it to `<service>/build/test-results/` and list that folder under `evidence.tests` in the manifest.

- pytest (built in): `python -m pytest --junitxml=build/test-results/pytest.xml`.
- unittest has no JUnit writer of its own. If the project already runs its tests with pytest, use the line above; otherwise a reporter package is an extra package a person must approve and add. You never install it.
