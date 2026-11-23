# Producer track: six stages

Each stage keeps every consumer working, can be undone on its own, and ends with build, tests and the gate for the next stage. **Run a stage's gate before you start the next stage**: the probes and the readiness report are part of each stage, not a step after all six. After each stage, set `producer.stage` in `tls-migration/tls-services.yaml`.

| Stage | Change | State afterwards | Gate to the next stage |
| --- | --- | --- | --- |
| 1 | Certificates and trust in place, kits sent ([consumer-kit.md](consumer-kit.md)) | no behaviour change | `cert-check.sh` has no failures |
| 2 | HTTPS listener **beside** HTTP (for example 8443 next to 8080). Client certificate `want`. One access-log line per request. Health probes moved to the management port (below). | every consumer still works; ready ones can move | P1 and P10 pass |
| 3 | Consumers switch on their own schedule ([consumer.md](consumer.md)) | mixed traffic | a readiness report ([cutover.md](cutover.md)) that shows no real caller with a certificate missing from the allowlist (`tls-probe-unlisted` aside): enforcing would turn such a caller away |
| 4 | Allowlist enforced for TLS callers: a valid certificate whose CN is not listed gets 403 | only allowed consumers succeed on TLS | P3 and P4 pass, **and** readiness says `ready_for_stage_5: true` (or a sign-off) |
| 5 | Client certificate `need` | HTTPS callers must present a certificate; plain HTTP still answers | readiness says `ready_for_stage_6: true` (or a sign-off) |
| 6 | Plain HTTP connector off: `tls.migration.legacy-http.enabled: false`, written out (`check.sh` does not accept a missing key); tests, scripts and docs updated | end state: mutual TLS only | `check.sh` |

Stage 3 lasts as long as the observation window: days or weeks. Stop there, say what you are waiting for and where the run stands (`producer.stage`), and pick the run up again when the log covers the window.

## Probe identity

P1 needs a certificate **and key** of an allowed caller at the probe location. In local that is a consumer's local certificate. In every other environment the producer run holds no consumer's key and must not make one: add the probe identity `tls-probe-allowed` to the allowlist and use its certificate ([certificates.md](certificates.md), "Probe certificates"). Its calls carry the probe header and never count as a consumer.

## The access-log line

The allowlist filter writes this line for every request, with the time in the message itself so no log format has to be parsed:

```text
tls-migration access ts=2026-11-14T05:10:00Z scheme=https client_cert=yes cn=orders allowed=yes probe=- path=/stock/SKU-1
```

- The line must be exactly this: the seven fields, once each, in this order, and nothing after `path`. The marker `tls-migration access` must start the message: at the start of the line, or right after the first ` : ` of the line (Spring Boot's default log pattern puts it after the logger name). Readiness rejects any other line that holds the marker, such as an application message that quotes it, and counts it in `rejected_lines`.

- `scheme` is `http` or `https`.
- `cn` is `-` when there is no certificate.
- `allowed` is `yes`, `no` or `n/a`.
- `probe=<id>` is the value of the `X-TLS-Migration-Probe` header when it matches `[A-Za-z0-9]{1,8}`, else `-`. The probes record the random tags they sent in `tls-migration/evidence/probe-tags.log`; readiness leaves out only those lines. A tagged call from anyone else is counted as what it is: plain HTTP, or HTTPS without a certificate.
- Point `producer.access_log` in the manifest at the file. `readiness-from-logs.sh` and `check.sh` read it.

## The allowlist

`tls-migration/allowed-consumers.yaml` lists consumer ids. The producer checks two things on every TLS call:

1. the client certificate chains to **this producer's** consumer CA (the TLS layer does this);
2. its CN is on the list (the filter does this).

A valid certificate whose CN is not listed gets 403. The filter reloads the file when it changes. To cut a consumer off, delete its line; nobody else needs a new certificate.

Before stage 4 the filter logs only. Deploy the allowlist file with the service, read-only. Its path comes from configuration.

## Health probes

With `need`, a platform probe with no certificate fails, and at stage 6 a probe on the plain port fails too. Move health to a management port without TLS **in stage 2**, limit that port to the node network, and name it in the plan. Keep every endpoint the service already exposed (metrics, info) reachable where its users expect it: say in the plan what moved. It is not an endpoint consumers call, so it is not an exception: `check.sh` requires P10 whenever `management.server.port` is set, and lists the health URL for review, not as a failure.

## Rollback per stage

| Undo | How |
| --- | --- |
| stage 6 | set `tls.migration.legacy-http.enabled: true` again; keep the connector code until one renewal cycle has passed |
| stage 5 | `client-auth: want` |
| stage 4 | allowlist in log-only mode (`tls.migration.allowlist.enforce: false`) |
| stage 3 | nothing to undo on the producer; a consumer that must go back points at the plain port again, which still answers |
| stage 2 | deploy the previous build and configuration (plain port as the main port, no TLS listener). Not `server.ssl.enabled=false` on the new build: the gate treats that as checking switched off |
| stage 1 | nothing to undo; certificates and kits can stay |

Write the rollback command for each stage you reach into the report. Rollback never means switching verification off on a consumer.

## Stack details

- Spring Boot: [java-spring.md](java-spring.md).
- Kubernetes: [kubernetes.md](kubernetes.md).
- Other stacks: the plan, certificates, kits and checks are the same, but you write the listener and filter changes by hand. Say so in the report.
