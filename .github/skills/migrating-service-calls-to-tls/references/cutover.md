# Cutover: readiness, sign-off, renewal

## Readiness report

Build it from the producer's access log; never from what consumer teams say:

```bash
<skill>/scripts/readiness-from-logs.sh --log tls-migration/evidence/inventory-access.log \
  --allowlist tls-migration/allowed-consumers.yaml --out tls-migration/evidence/readiness.json \
  --md tls-migration/consumer-readiness.md --min-observation-days 14 \
  [--signoff tls-migration/cutover-signoff.yaml --signoff-roles "producer service owner"]
```

Take `--min-observation-days` from the policy file: `environments.<env>.min_observation_days`, else `cutover.min_observation_days`. Outside `local` the policy is the one the operator hands to the gate (`check.sh --policy <file>` or `TLS_POLICY`), not one the run names, and the window is never under 7 days whatever the file says. It is never negative.

## Rules

- **When a consumer is ready.** It has been seen on mutual TLS with its own CN within its window.
- **The window.** `max(min_observation_days, cadence + 7 days)`. A monthly batch consumer that hasn't run yet is not ready just because nobody saw it fail.
- **The log must cover the window.** A log reaching back two days proves nothing about a monthly consumer.
- **Plain-HTTP calls carry no certificate,** so they can't be pinned on a consumer. Any plain-HTTP call in the longest consumer window blocks stage 6: a monthly batch that still runs over HTTP is seen even when the observation period is 14 days.
  - In `local` (no window) it counts the calls made after every consumer had moved.
- **`verify-result.json` is supporting evidence only.** It proves a consumer **can** connect, not that it **has** switched. The kit's `verify.sh` marks its request with a fresh random tag in `X-TLS-Migration-Probe` (its `probe_tag`), and a marked call never shows that a consumer has moved.
- **Only the gate's own probes are left out.** `probe-tls.sh` and `check.sh --live` send a fresh random tag in `X-TLS-Migration-Probe` and record it in `tls-migration/evidence/probe-tags.log`. Readiness leaves out the lines with a recorded tag and nothing else: anyone can send that header, so a tagged call over plain HTTP still counts as plain HTTP, and a tagged call without a certificate still counts as one.
- **The probe identity is not a consumer.** `tls-probe-allowed` ([certificates.md](certificates.md)) is on the allowlist for P1 only; its calls are probes.
- **A sign-off can override.** Use `tls-migration/cutover-signoff.yaml`:

  ```yaml
  signed_by: "name of the person"
  role: producer service owner      # must be one of the policy's cutover.signoff_roles
  date: 2026-11-20
  accepted_unready: [billing]       # consumers accepted as breaking
  accepted_http_calls: false        # true to close HTTP although calls were seen
  accepted_certless_calls: false    # true to require certificates although HTTPS calls without one were seen
  ```

  You never write this file. A person in the role writes it.

  **A sign-off is text in the repository.** The gate checks that `signed_by`, `role` and `date` are filled in and that the role is one of the policy's `cutover.signoff_roles`. It cannot tell who wrote the file: anyone who can write to the repository, an assistant included, can write one. The same holds for `approved_by` in `exceptions.yaml`. Whoever relies on a `pass with exceptions` confirms each sign-off and each approval with the person named. The verification judge lists every one as "not verified: who wrote it".

## Gates

- **Stage 5** (client certificate `need`) needs `ready_for_stage_5: true`, as well as P3 and P4.
- **Stage 6** (plain HTTP closed) needs `ready_for_stage_6: true`.
- `check.sh` rebuilds readiness from the log itself (E8); it doesn't trust `readiness.json`.

## Renewal and revocation

| Event | Producer | Consumer |
| --- | --- | --- |
| Server certificate renewal | cert-manager `renewBefore`, or Vault and a script; hot reload. In `test-certificates` mode nothing re-runs `certgen-test-ca.sh` or `make-server-cert.sh` automatically: the producer team owns this and schedules it (a calendar reminder or a CI job) before `renew_before_days`; `cert-check.sh` fails a certificate at 21 days by default | nothing, while the CA stays the same |
| Client certificate renewal | signs the new CSR | `make-csr.sh --renew` once (a new key in `client.key.next`; the key in use stays); the new certificate is saved as `client.crt.next` (never over `client.crt`, which is in use); then `make-csr.sh --activate --cert client.crt.next`, which checks that the certificate belongs to the new key and swaps both together; then **restart the consumer** (or update its Secret and roll it) |
| Consumer CA rotation | `certgen-test-ca.sh` keeps the old CA certificate beside the new one; the trust file holds both during the overlap ([certificates.md](certificates.md), "CA rotation"); the old one drops out when it expires | renew before the old CA expires |
| Server CA rotation | rebuild the kits with both CAs (`--server-ca server-ca.current.crt --previous-server-ca server-ca.previous.crt`) and send the new SHA-256; re-issue the server certificate with `--after-overlap` only once every consumer has sent a `verify-result.json` from the rebuilt kit with `"ca_overlap": true` and `"ok": true` ([certificates.md](certificates.md), "CA rotation") | deploy the rebuilt kit's `ca-bundle.pem` (it holds both CAs); restart; run `verify.sh` and send `verify-result.json`; take the next kit, with the new CA alone, after the old one has expired |
| Revoke a consumer | delete its line from `allowed-consumers.yaml`; the filter reloads and blocks at once | none |

A renewed **server** certificate is picked up by the producer's embedded server without a restart (Spring Boot 3.2+, `reload-on-update`). A renewed **client** certificate is not: an HTTP client reads its certificate once, when it is built ([java-spring.md](java-spring.md)). Write the restart into the renewal steps you hand over.

There is no CRL or OCSP in this version. Short lifetimes and the allowlist limit the risk; say so in the report.
