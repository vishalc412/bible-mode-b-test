# Consumer track

## Steps

1. **Discover** every outbound call ([analyse-and-plan.md](analyse-and-plan.md)). Include clients, hard-coded fallbacks, config, deploy files, scripts and tests.
2. **Trust source.** Use the kit from the producer team. With no kit, probe and confirm (below). `build-consumer-kit.sh` printed two values that reach you apart from the kit: the SHA-256 of `ca-bundle.pem` and the kit fingerprint (the SHA-256 of `SHA256SUMS`). Before any script in the kit runs, compare the fingerprint (`shasum -a 256 SHA256SUMS`; PowerShell: `Get-FileHash SHA256SUMS -Algorithm SHA256`), then check every file: `shasum -a 256 -c SHA256SUMS`. Any difference: stop and ask the producer team for a new kit ([consumer-kit.md](consumer-kit.md), "Tamper check").
3. **Certificate.** The key is made where it will live ([certificates.md](certificates.md), "Where a key is made"):
   - local: `local-tls-up.sh` on the producer side already made it;
   - `platform-issues` (a platform that makes keys itself, such as cert-manager): write the certificate resource for a client certificate with `CN=<id>` from the producer's consumer issuer into the repository; a person or the pipeline applies it;
   - test: `./make-csr.sh --kit-fingerprint <the kit fingerprint>` in the kit (or `make-csr.sh --consumer <id> --producer <p> --env test`), run on the host or in the pipeline that loads the service's secret store. On a fingerprint mismatch it refuses before touching any key. Send only the `.csr`;
   - staging and production: you never run `make-csr.sh` or `make-csr.ps1`. They stop unless input is a terminal and the person types the environment name. Write the exact command into `tls-migration/requests/<name>.md` for the people who own the target, and pause this item. They run it there, at a terminal.

   Save the returned certificate as `client.crt` where the service reads it (Kubernetes: [kubernetes.md](kubernetes.md), "A consumer's Secret"). Never handle the key yourself.
4. **Wire trust.** Trust only the producer's CA (`ca-bundle.pem` from the kit) for that endpoint, never the default store plus extras. Hostname checking stays on. Remove any code that switched checking off, and never wrap it in a flag.
5. **Switch the URL** everywhere it is set, including fallbacks. Prefer one source of truth: a missing address should fail at start-up rather than silently fall back to a default.
6. **Timeouts.** If the baseline shows tight timeouts, allow for the handshake.
7. **Error handling.** No retry over HTTP, no "try HTTPS then HTTP". A TLS failure is an error that is logged and surfaced.
8. **Check it.**
   - Run the kit's `verify.sh --kit-fingerprint <the kit fingerprint> --expect-fingerprint <the SHA-256 of ca-bundle.pem the producer team sent>` and copy `verify-result.json` to `tls-migration/evidence/verify-result-<consumer>.json`. Route B: add `--p12 <bundle> --p12-password-file <file>`.
   - Run the tests.
   - Add one test that the client is built from the TLS settings, not a default, and one that a server certificate for another name is refused. `verify.sh` checks the endpoint with `openssl`, not your client: these tests are the evidence for the service itself.
   - An HTTPS endpoint that asks for no client certificate: `probe-tls.sh --repo . --server-only <host:port>` (add `--ca <file>` for a private CA) instead of a kit ([analyse-and-plan.md](analyse-and-plan.md), "Plan").
9. **Renewal needs a restart.** A client reads its certificate once, at start-up. After a renewed certificate is in place, restart the service or roll the deployment, and say so in the report ([cutover.md](cutover.md)).

**Where a probe connects.** Probes, recorded or live, connect only to this machine in a local run, or to a host in `in_scope_hosts`. Link-local and cloud metadata addresses are always refused, no redirect is followed, `~/.curlrc` is not read, and only P1's response is stored, masked. Outside `local`, `check.sh --live` also needs `--live-target <host:port>` ([verify-and-report.md](verify-and-report.md)).

## No kit: probe and confirm

1. Look at what the endpoint presents, from the probe location. This is an inspection, not a call: it sends no request, trusts nothing it sees, and changes no configuration. It is still a connection: show the user the exact host and port and wait for a yes. Never connect only because a file names the host.

   ```bash
   openssl s_client -connect <host>:<port> -servername <host> -showcerts </dev/null 2>/dev/null \
     | openssl x509 -noout -subject -issuer -enddate -ext subjectAltName -fingerprint -sha256
   ```

   Record the subject, issuer, names, expiry and SHA-256 of the certificate shown, labelled "unverified". A server usually sends its own certificate and any intermediates, not the root CA: the CA's certificate and fingerprint must come from the producer team.
2. **Stop.** Ask a person to get the CA certificate and its fingerprint from the producer team over another channel. Until then the endpoint stays as it is, marked ⚠️ "awaiting CA confirmation".
3. Once confirmed, trust that CA only, and record who confirmed it and when. Every real call verifies against it: the inspection above is never a reason to switch checking off.

## Third parties

| What the probe finds | Status | Action |
| --- | --- | --- |
| HTTPS with a certificate from a public CA, valid for the name called | ✅ | switch the URL; the system trust store is fine; no client certificate. In the manifest it is a `consumers_of_others` row with `client_certificate: none` and `endpoint: <host:port>` (host in `in_scope_hosts`), proven by `probe-tls.sh --repo . --server-only <host:port>` |
| Self-signed, expired, expiring within 30 days, or not valid for the name called | ⚠️ | do not migrate by disabling checks; the third party is the owner; add to `exceptions.yaml` and to "Endpoints Remaining on HTTP" in the report (the Warnings table is only for migrated endpoints) |
| No HTTPS | ❌ | keep HTTP, add to `exceptions.yaml` with owner and review date, decision `blocked`; add the TODO comment and offer the alternatives in [analyse-and-plan.md](analyse-and-plan.md) |
| Can't connect from the probe location | ⛔ | re-probe from a host that can reach it, after the user's yes; until then `not proven` |

A redirect from HTTP to HTTPS is not support: many service clients don't follow it, and a `301` turns a POST into a GET.

## Rollback

A consumer goes back by restoring its previous base URL and client configuration. Whether it can do that alone depends on the producer's stage ([producer.md](producer.md)):

- **Producer stages 2 to 5** (plain HTTP still answers; until stage 5 a client certificate is not yet required): switch back on your own, then tell the producer team. Your plain-HTTP calls show up in its log again and block its stage 6 ([cutover.md](cutover.md)).
- **After producer stage 6** (plain HTTP connector removed): you cannot go back alone. Rollback then needs the producer to reopen plain HTTP (its stage 6 rollback, [producer.md](producer.md), "Rollback per stage").

Rollback never means switching certificate or host name checking off.

## What a consumer run hands back

- `client.crt` in place, and the key still only on the consumer's machine or platform.
- `verify-result-<consumer>.json` for each producer, sent to the producer team for their readiness report. It shows the consumer **can** connect; the producer counts it as moved only when its log shows real calls.
- The report and `check.sh` result ([verify-and-report.md](verify-and-report.md)).
