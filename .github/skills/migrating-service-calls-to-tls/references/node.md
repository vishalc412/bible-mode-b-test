# Node.js

Contents: producer · consumer · files and local · never do this · tests

The gate's E12 reads Spring Boot configuration only. For this stack E12 reports `not run: stack not read (<stack>)`, so the overall result is at best `not proven` until a person or the judge checks these settings.

Written for Node 18 and later with the built-in `node:https` and `node:tls` modules. Express and similar frameworks sit on the same server object. Record the Node version from `package.json` (`engines`) or the runtime image first.

## Producer

Stage settings come from the environment, never from code constants. Suggested names, used the same way on every stack page: `TLS_CLIENT_AUTH` (`want` stages 2-4, `need` from stage 5), `TLS_LEGACY_HTTP_ENABLED` (`true` stages 2-5, `false` stage 6), `TLS_ALLOWLIST` (file path), `TLS_ALLOWLIST_ENFORCE` (`false` stages 2-3, `true` from stage 4). Write the values in the deploy files so a person can read them.

```js
const fs = require("node:fs");
const https = require("node:https");
const dir = process.env.TLS_DIR, keyDir = process.env.TLS_KEY_DIR;   // no defaults: fail at start-up
const need = process.env.TLS_CLIENT_AUTH === "need";
const server = https.createServer({
  cert: fs.readFileSync(`${dir}/tls.crt`),
  key: fs.readFileSync(`${keyDir}/tls.key`),
  ca: fs.readFileSync(`${dir}/consumers-ca.crt`),   // this producer's consumer CA only
  minVersion: "TLSv1.2",
  requestCert: true,
  rejectUnauthorized: need,                          // see the note below
}, app);
```

- **The `want` stages (2-4) are a known gap.** Node has no "ask, but do not require" switch: asking without requiring means `rejectUnauthorized` is false on the server during those stages. The scanner cannot tell this server setting from a client that switched checking off, so list the line in the report for a person to review, and never copy the pattern into a client. During stages 2-4 the middleware must treat `req.socket.authorized === false` as "no certificate" (`cn=-`). From stage 5 the value is `true` and the TLS layer refuses callers without a valid certificate.
- **Allowlist and access line,** in one middleware that runs first: take the CN from `req.socket.getPeerCertificate().subject.CN` only when `req.socket.authorized` is true; check it against the allowlist file (re-read when it changes; an unreadable file allows nobody); write the access line from [producer.md](producer.md) with `probe=<id>` taken from the `X-TLS-Migration-Probe` header only when it matches `[A-Za-z0-9]{1,8}`, else `-`; answer 403 for an unlisted CN when enforcing.
- **Plain HTTP (stages 2-5):** a second `http.createServer(app)` started only when `TLS_LEGACY_HTTP_ENABLED` is `true`. At stage 6 the variable is written out as `false`.
- **Health:** a separate plain listener on the management port, bound to the node network, serving health only.
- **Renewal:** `server.setSecureContext({...})` swaps the certificate without a restart; otherwise restart after each renewal and say so in the report.
- Tests: listed consumer served; unlisted gets 403; log-only mode serves; a removed line cuts the consumer off; a missing allowlist file allows nobody.

## Consumer

```js
const agent = new https.Agent({
  cert: fs.readFileSync(`${process.env.TLS_DIR}/client.crt`),
  key: fs.readFileSync(`${process.env.TLS_KEY_DIR}/client.key`),
  ca: fs.readFileSync(`${process.env.TLS_DIR}/ca-bundle.pem`),   // replaces the default CAs: the producer's CA only
  minVersion: "TLSv1.2",
});
const baseUrl = process.env.INVENTORY_BASE_URL;
if (!baseUrl || !baseUrl.startsWith("https://")) throw new Error("INVENTORY_BASE_URL must be set to an https:// URL");
```

- Pass `agent` to every call (`https.request(url, { agent })`). Libraries such as axios take `httpsAgent: agent`. The built-in `fetch` (undici) does not take an `https.Agent`: it needs undici's own dispatcher with the same `connect` options. Check the version you use, and test that the certificate is really sent.
- Host name checking is on by default. Leave `checkServerIdentity` alone.
- A client reads its certificate once: restart after a renewal.
- Tests: the client is built from these files; a blank or `http://` address is refused; a server certificate for another name is refused.

## Files and local

- Paths come from the environment (`TLS_DIR`, `TLS_KEY_DIR`). Certificates may live in the repository's local folder; keys never do and are never committed.
- Local: certificates from `tls-migration/local/certs/` (`<producer>-server.crt`, `<producer>-consumers-ca.crt`, `server-ca.crt` as the consumer's `ca-bundle.pem`, `<producer>-<consumer>.crt`); keys `$TLS_PRIVATE_DIR/local/<producer>/server.key` and `$TLS_PRIVATE_DIR/local/<producer>/<consumer>/client.key`. Put these paths only in local-only files (`.env.local`, `docker-compose.local.yml`): E10 fails `local-dev-` references anywhere else.
- A call that must stay on plain HTTP gets exactly `// TODO: HTTPS not supported - requires infrastructure update` beside it ([analyse-and-plan.md](analyse-and-plan.md)).

## Never do this

None of these may appear, not even in tests. The gate's scanner looks for most of them; a person or the judge checks the rest:

- `rejectUnauthorized: false` on a client, `strictSSL: false`;
- `NODE_TLS_REJECT_UNAUTHORIZED=0`, in code, scripts, Dockerfiles or deploy files;
- `checkServerIdentity: () => undefined` or any function that skips the name check;
- `minVersion: "TLSv1"` or `"TLSv1.1"`, `secureProtocol: "TLSv1_method"`;
- `curl -k` / `--insecure` in scripts.

## Tests and JUnit XML

E1 reads JUnit-style XML only. Write it to `<service>/build/test-results/` and list that folder under `evidence.tests` in the manifest.

- Built-in runner (Node 20.13 / 21.3 and later; check the version you use): `node --test --test-reporter=spec --test-reporter-destination=stdout --test-reporter=junit --test-reporter-destination=build/test-results/node-test.xml`.
- Jest: needs the `jest-junit` package. If the project does not already have it, it is an extra package a person must approve and add; you never install it. Then `JEST_JUNIT_OUTPUT_DIR=build/test-results npx jest --reporters=default --reporters=jest-junit`.
- Vitest: `npx vitest run --reporter=junit --outputFile=build/test-results/vitest.xml`.
