# Steps 7 to 9: verify, report, gate

Contents: 7. Verify · 8. Report · 9. Gate and hand-over · what the gate cannot see · what the result means

You run scripts and quote what they wrote. You never decide a check result yourself, and you never edit an evidence file.

## 7. Verify

**Certificates:**

```bash
<skill>/scripts/cert-check.sh --repo . --plan tls-migration/certs-to-check.yaml --out tls-migration/evidence/certs.json
```

**Probes** (producer and both). Write `tls-migration/probe-plan.yaml` (format in the header of `scripts/probe_tls.py`), then run it from the probe location. In `local` the probes connect to this machine only. Anywhere else, show the user the exact host and port from the probe plan and wait for a yes:

```bash
<skill>/scripts/probe-tls.sh --repo . --plan tls-migration/probe-plan.yaml --out tls-migration/evidence/probes.json
```

| # | Probe | Expected |
| --- | --- | --- |
| P1 | allowed consumer, correct certificate, real request (in `local` a consumer's certificate from `local-tls-up.sh`; elsewhere the allowlisted probe identity `tls-probe-allowed`, `probe-<env>/<producer>/probe-allowed.crt`, see `certificates.md`) | a 2xx status, and the same answer as the baseline (the plan's `baseline:` must cover the path); the client certificate is a planned one or `tls-probe-allowed` |
| P2 | no client certificate | stage 5 onward: refused; before: answered |
| P3 | certificate from the untrusted negative-test CA | refused |
| P4 | valid certificate, CN not on the allowlist | stage 4 onward: 403 |
| P5 | TLS 1.0 and 1.1 offered | refused |
| P6 | weak cipher suites | refused |
| P7 | plain HTTP port | stage 6: closed; before: answers |
| P9 | presented chain | planned issuer, TLS 1.2+, every planned name, not expiring soon |
| P10 | health probes without a certificate | healthy on every attempt |

How the probes are judged:

- **Refusals need a working service.** They count only when P1 passed; otherwise they are `not run`, because a refusal can't be told from an outage.
- **Not tested is not run.** A probe the local openssl can't even attempt is `not run`, never pass.
- **Every probe sends a real request.** Under TLS 1.3 a rejected client certificate shows only on the first read.

**Timing.** The baseline and P1 record the total request time and, over TLS, the handshake time in ms (`total_ms`, `handshake_ms`). The report shows them before and after. Timing never fails the gate; a slowdown above the policy's `max_latency_increase_pct` becomes a Warnings row.

**Consumers.** Run `verify.sh` from the kit and keep `verify-result-<consumer>.json`.

**An HTTPS endpoint that asks for no client certificate** (a third party with a public CA). In the manifest it is a `consumers_of_others` row with `client_certificate: none` and `endpoint: <host:port>`; its host must be in `in_scope_hosts`. Show the user the exact host and port, wait for a yes, then:

```bash
<skill>/scripts/probe-tls.sh --repo . --server-only <host:port>        # --ca <file> for a private CA
```

`--ca` works in every environment, but only for this probe. Outside `local`, `check.sh` does not count the recorded file and does not use a CA from the repository: `check.sh --live` re-checks the endpoint against the system's trusted CAs. The probe prints a note saying so.

It checks the certificate and the host name, offers no client certificate, needs TLS 1.2 or later, and writes `tls-migration/evidence/server-only/<host>_<port>.json` (protocol, cipher, certificate subject, issuer and end date, verify result, total and handshake ms). E6 accepts that file for the row instead of a kit's `verify-result.json`. A row for an endpoint this repository's producer serves fails: the producer asks for client certificates.

**Readiness** (producer, before stages 5 and 6). See [cutover.md](cutover.md).

## 8. Report

Write `tls-migration/03-migration-summary.md`. It keeps the required headings, with evidence for every line. `check.sh` (E11) parses it, so keep these headings and labels exactly:

```markdown
# HTTPS Migration Summary Report: <producer|consumer|both> <service>, <environment>, <date>

Overall result: <the result check.sh printed>

## Successfully Migrated Endpoints
| Endpoint | Role | Certificate (issuer, expires) | Renewal | Evidence |
| --- | --- | --- | --- | --- |
| https://localhost:8443/stock/{sku} | we produce | local-dev-server-ca, 2026-12-14 | local-tls-up.sh | probes.json#P1, probes.json#P9 |

## Endpoints Remaining on HTTP
| Endpoint URL | Reason | Priority | Action Required | Owner | Review date |
| --- | --- | --- | --- | --- | --- |

## Endpoints with Warnings
| Endpoint URL | Warning | Recommended Action |
| --- | --- | --- |
| none | | |

## Not proven
| Endpoint | Check | Reason not run | Who can run it |
| --- | --- | --- | --- |

## Timing
| Endpoint | Before (ms) | After (ms) | TLS handshake (ms) |
| --- | --- | --- | --- |

## Consumers
Link to consumer-readiness.md (producer runs). Key travelled (route B): list, or "none".

## Rollback
One line per stage reached.

## Statistics
- Total: N endpoints
- Successfully migrated: Y (Z%)
- Remaining on HTTP: A (B%)
- Blocked by infrastructure: C
- Not proven: D
```

Rules for the report:

- **"Migrated" needs evidence.** A row counts only when its Evidence cell cites a passing probe (`probes.json#P1`), a `verify-result-<consumer>.json` that shows `ok`, or a passing `server-only/<host>_<port>.json` of a server-only row, **for the endpoint the row names**: the host of the row's URL must be the host the probes targeted (or the endpoint the verify-result called), under any of its names; on a laptop, where the probes target this machine, the producer's own names count too. A row written in words ("orders to inventory") must name that host. A URL that was merely edited is not migrated.
- **Outside `local`, a consumer row needs the consumer's own certificate.** P1 there uses the probe certificate, so a `we consume (<consumer>)` row also needs `verify-result-<consumer>.json` from the kit (in `tls-migration/evidence/`, or `verify-result.json` in the kit folder) showing `ok` for that CN, or the producer's access log showing `cn=<consumer>` let through over mutual TLS. Without either, E11 fails: "no evidence that <consumer>'s own certificate was used". Name the consumer in the Role cell.
- **The two lists must agree.** "Remaining on HTTP" has exactly the rows in `exceptions.yaml`: the same URLs, not just as many. Keep the section even when nothing stays on HTTP, with an empty table: a report without it fails.
- **Endpoints with Warnings** has one row per migrated endpoint that passed with a warning: a certificate that expires within 30 days (a `local-dev-` certificate in `local` is left out: it lives 30 days by design), TLS 1.2 where the policy's `certificates.preferred_tls_version` is 1.3, a cipher outside `certificates.preferred_ciphers`, or a slowdown above `max_latency_increase_pct`. E11 works these out from what E6 observed and requires a row for each; write `none` when there are none. A Warnings row is counted inside "Successfully migrated", so it must name a migrated endpoint. An endpoint that cannot move (self-signed, expired, no HTTPS) stays on HTTP: it goes to "Remaining on HTTP".
- **Blocked by infrastructure** counts the rows of "Remaining on HTTP" whose inventory decision (`01-inventory.md`, column Decision) is `blocked`. Each blocked endpoint's plain-HTTP line carries `TODO: HTTPS not supported - requires infrastructure update` on it or in the three lines above. "Remaining on HTTP: A" counts the other rows of that table.
- **Statistics are counted from the tables,** not estimated: `Total: N endpoints` is migrated + remaining + not proven + blocked; migrated and remaining show their share of N in whole per cent (checked within 1 point).
- **Keep every section.** Warnings, Consumers and Rollback must be there (Consumers and Rollback not empty); E11 fails without them.
- **The overall result never claims more than `check.sh`.** A local run says "proven locally".

## 9. Gate and hand-over

```bash
<skill>/scripts/check.sh --repo .                                                       # local
<skill>/scripts/check.sh --repo . --live --live-target <host:port> --policy <file>      # test, staging, production
```

Outside `local` the person who runs the gate hands it the policy file (`--policy`, or the environment variable `TLS_POLICY`), kept outside the repository: the gate refuses a policy file inside `--repo`. The manifest's own `policy:` line counts in `local` only: a run does not choose the rules it is judged by.

`check.sh --live --live-target <host:port>`: required outside `local`; host and port must equal the probe plan's target (or, for a consumer, the kit's endpoint, or a server-only row's endpoint), else E6 fails and nothing is sent. Give it once per endpoint the run connects to. In `local` it is optional and checked when given. Before `--live`, show the user the exact host and port and wait for a yes.

`check.sh` writes `tls-migration/evidence/check-result.json` and prints one line per check:

| Id | Check |
| --- | --- |
| E0 | The manifest exists and names role, environment, stage and `migrator_model`. |
| E1 | Tests ran and pass in every in-scope module, and their reports are newer than the code they test. A skipped test never counts as passed. Another stack's reports come from `evidence.tests`. |
| E2 | No plain `http://` to an in-scope host, under any of its names or built at run time, outside `exceptions.yaml`; the scope matches what discovery recorded, and every plain-HTTP host the scan finds now is in that record. |
| E3 | None of the known ways of switching certificate checking off, or allowing old protocols, is in code or config. Pattern matching: it cannot prove checking is on. |
| E4 | No private key or key store anywhere in the tree, found by name, PEM block, content and structure, archives and encodings included. |
| E5 | Every certificate re-checked from the files: names, issuer, lifetime and renewal margin from the operator's policy; no `local-dev-` or `test-` CA outside its environment. |
| E6 | Probe results re-derived from what was observed, bound to the config, code, plans and certificates; server-only rows from their evidence file; outside `local` only `--live` to the operator's confirmed target proves anything. |
| E7 | Each trust store holds only the planned CA, and each service's configuration names the planned store for its side. |
| E8 | Stages 5 and 6 only with readiness rebuilt from the access log, or a sign-off (then at best `pass with exceptions`). |
| E9 | Each kit is complete, matches `SHA256SUMS`, the toolkit's own files and the plan, holds no key, and its `ca-bundle.pem` is the planned server CA. |
| E10 | No `local-dev-` CA outside local-only files, by name, fingerprint or parsed certificate, build output included. |
| E11 | The report matches the evidence: migrated rows cite passing evidence for that endpoint; "Remaining on HTTP" equals `exceptions.yaml`; the Total line, percentages, Blocked count and Warnings rows add up; Warnings, Consumers and Rollback are there. |
| E12 | The producer's configuration, read the way Spring reads it (`SERVER_SSL_CLIENTAUTH` and `SERVER_SSL_CLIENT_AUTH`: Spring binds both), matches its stage; every Spring consumer, the producer's own outbound client included, builds its client from an SSL bundle with a key store. Another stack: `not run: stack not read (<stack>)`. |
| E13 | Every exception names one host, an owner, a reason, a future review date, and a second person's `approved_by` where required; every `out_of_scope` entry has a reason. |
| E14 | The producer cutover reached stage 6. |
| E15 | Every file that could change a verdict was read; what could not be read is listed under `skipped`, and a blocking one makes the result `not proven`. |

The full rules of each check are in [gate-checks.md](gate-checks.md). E3 is pattern matching: never quote an E3 pass as "certificate checking is on"; the verification judge owns that question.

### What the gate cannot see

- **The access log is a file.** E8 rebuilds readiness from the log the manifest names. Nothing ties that file to the real producer; a person who knows where the log came from confirms it.
- **Probe tags.** `probe-tls.sh` and `check.sh --live` tag their own requests with a fresh random tag and record it in `evidence/probe-tags.log`. Readiness leaves out only recorded tags; any other tagged line counts as ordinary traffic over plain HTTP or without a certificate, and never shows that a consumer has moved.
- **Addresses and settings made at run time.** A URL built in code, or a setting read from a Secret, is failed or left `not run`; the gate does not guess.
- **A library outside the repository.** E12 and E7 read the config of modules the build depends on only when they are in this repository; a library from a registry that ships `application.yml` is not read (a dependency on an unknown module of the same group is `not run`, any other group is not).
- **Rotation files are trusted by name.** A CA in `<store>.previous.crt` / `.current.crt` beside a trust store, or in `previous_ca:`, counts as declared; whoever can write the plan can write those. E7 lists them in its evidence.
- **The bare key marker.** A key assembled at run time from pieces is found by its marker; one whose marker is itself built from pieces is not. Code that only names the marker (a key parser) fails outside dependency installs; the verification judge decides.
- **Unparsable files are not guessed.** A Helm template or other YAML that does not parse and names a watched setting makes E12 `not run` until it is rendered or listed out of the run.
- **`--live` proves the host it reached.** Outside `local` that host must be in `in_scope_hosts` and equal the operator's `--live-target`; that the name resolves to the real service is the operator's to know.
- **Sign-offs and approvals are text in the repository.** E8 and E13 check that `cutover-signoff.yaml` and `approved_by` are filled in, that the role is a policy role and that the approver is not the owner. They cannot tell who wrote the file: the migrating assistant could have. Whoever relies on a `pass with exceptions` confirms each one with the person named ([cutover.md](cutover.md)).
- **Patterns, not proof.** E2, E3 and E4 find the forms they know. A form they do not know passes them; the verification judge reads the code for that.

What the result means:

- **`fail`:** anything failed.
- **`not proven`:** nothing failed, but something did not run.
- **`pass with exceptions`:** everything ran and passed, and some endpoints stay on HTTP in `exceptions.yaml`, or a sign-off accepted consumers that were not ready.
- **`pass`:** everything ran and passed.

A check that crashes is a `fail` with the reason. The result file (`check-result.json`, or the file `--out` names) is written as `fail` before the first check runs and replaced at the end, so a run that is stopped half-way never leaves an older pass behind in it. With `--out` somewhere else, the repository's own `check-result.json` is not touched: it is not this run's result. A mistyped command line, or an `--out` that is a folder, is exit 3 (bad input); a mistyped one also leaves a `fail`.

What to do with it:

- **Fix the cause** of a failure, then run the gate again. Never edit evidence, the report or the manifest to get past a check.
- **Quote the result** to the user exactly as printed.
- **Hand over.** Tell the user to run `verifying-a-tls-migration` in a new session on a different model line, as their operator defines it (the judge skill's `references/report.md`, "Independence"), which judges what a script can't. Your run is finished only after that verification.
