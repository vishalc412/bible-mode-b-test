# Local catalog–orders mutual-TLS plan

Planning only: no certificate, key, listener, client, kit, probe, baseline, test report or gate result has been created by this step. The owner confirmed the inventory and the decisions below. The earlier analysis status check returned exit 20, `UNVERIFIED (COMPONENTS_VERIFIED)`; the whole-analysis verification report and `codebase-analysis/knowledge/graph.json` are absent. A graph-backed `assessing-change-impact` assessment cannot run until the analysis is assembled and verified and the graph exists. The impacts below are source-confirmed, not a substitute for that assessment.

## Confirmed local inputs

- Catalog is the Python 3 standard-library `ThreadingHTTPServer` producer; orders is its Python `urllib` consumer. Discovery used Python 3.12.3.
- HTTPS listener: `127.0.0.1:8443`; retain configurable `CATALOG_HOST` and `CATALOG_PORT`. During transition retain HTTP on `127.0.0.1:8001`; ensure the two listener ports can be configured independently.
- Server SANs: DNS `localhost`, IP `127.0.0.1`, DNS `catalog`. These are certificate names, not an assertion that `catalog` resolves on the laptop.
- Owner decision: `/health` has no consumer except tests and remains on the same listener, moving to mTLS with it; no separate management port. This differs from the skill's producer guidance requiring a separate management listener. Reconcile this deviation with the later stage-2/P10 verification before implementation; do not claim that check passed or invent a health listener.
- One allowed consumer: `orders`; owner: orders team; contact: repository owner; cadence: per order. The owner chose the test suite as the local observation. The readiness script does **not** recognize `per order`: it marks that cadence unready even in local mode. A successful test run alone does not satisfy the automated readiness rules: the producer log must show an allowed, non-probe mTLS call from `orders`, and any unready consumer or remaining HTTP calls require a valid owner-role sign-off where applicable. Resolve the cadence/tooling mismatch with the owner before cutover; do not silently relabel the cadence or generate a sign-off.
- Supplier feed and payment endpoints remain out of scope (issue #75). `localhost:8099` is a payment fake, not catalog. Since `localhost` is also an in-scope catalog name, the gate's host-level scan may flag that unrelated URL; resolve this scope collision without weakening verification or treating it as a catalog call.

## Certificates and trust

Mode: local `test-certificates`, with no policy file. Keys are created only on the developer laptop, outside the repository in `$TLS_PRIVATE_DIR`; scripts handle them. Public files are local-only and no local CA is installed system-wide.

| Service | Presents | Names | Issuer | Mode | Key made by | Delivered how | Renewal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| catalog | Server leaf, `serverAuth` | DNS `localhost`, IP `127.0.0.1`, DNS `catalog` | `local-dev-server-ca` | local test-certificates | `local-tls-up.sh` on the laptop | Public certificate in `tls-migration/local/certs/catalog-server.crt`; key at `$TLS_PRIVATE_DIR/local/catalog/server.key` | Local leaf lifetime 30 days; rerun the local tooling before expiry and restart catalog after renewal. |
| orders | Client leaf, `clientAuth` | CN `orders`; URI `spiffe://<trust-domain>/consumer/orders` | `local-dev-catalog-consumers-ca` | local test-certificates | `local-tls-up.sh` on the laptop | Public certificate in `tls-migration/local/certs/catalog-orders.crt`; key at `$TLS_PRIVATE_DIR/local/catalog/orders/client.key` | Local leaf lifetime 30 days; renew through the tooling and restart orders after activation. |
| refusal probe | Unlisted client leaf, `clientAuth` | CN `tls-probe-unlisted` | `local-dev-catalog-consumers-ca` | local test-certificates | `local-tls-up.sh` on the laptop | Probe files under `$TLS_PRIVATE_DIR/probe-local/catalog/` | Regenerate with the local tooling as needed; never add this identity to the allowlist. |
| refusal probe | Untrusted client leaf, `clientAuth` | CN `tls-probe-untrusted` | `local-dev-negative-test-untrusted-client` | local test-certificates | `local-tls-up.sh` on the laptop | Probe files under `$TLS_PRIVATE_DIR/probe-local/catalog/` | Regenerate with the local tooling as needed; never trust its CA. |

Catalog trusts only its consumer CA and checks the certificate CN against the allowlist. Orders trusts only the local server CA, verifies the server name, presents its own client certificate and uses TLS 1.2 or newer. No HTTP fallback or verification bypass. The local CAs have 90-day lifetimes; follow the toolkit's overlap procedure for CA rotation and restart these Python processes after renewal. There is no CRL or OCSP in the toolkit; use short lifetimes and allowlist removal to limit exposure.

The trust domain has not been supplied; select and record it in the allowlist before issuance, rather than inventing it. Only the two requested planning files are created now: `tls-migration/allowed-consumers.yaml`, the probe plan, kits, certificate check plan and evidence referenced by the manifest are **future artifacts**, not present or validated. Before issuance create the allowlist with producer `catalog`, identity `orders`, the owner/contact and the owner's actual cadence, and agree how the readiness tool will handle that cadence. The local tooling normally selects `~/.tls-migration/private/<repo>-<8 hex of its path>` when `TLS_PRIVATE_DIR` is unset, or uses an approved exported external directory; the developer must confirm the actual directory before making keys.

After those prerequisites and plan approval, the developer may run the following from the repository root on the laptop, not in this planning session. The script also updates the repository's `.gitignore` for local artifacts:

```bash
.github/skills/migrating-service-calls-to-tls/scripts/local-tls-up.sh \
  --repo . --producer catalog --allowlist tls-migration/allowed-consumers.yaml \
  --names "localhost,127.0.0.1,catalog"
export TLS_PRIVATE_DIR="$(cat tls-migration/local/private-dir.txt)"
```

## Source-confirmed impact and proposed sequence

1. Baseline later, after approval: `python3 -m unittest discover -s . -p "test_*.py" -t .`; the developer starts the existing catalog service bound to `127.0.0.1` and runs the HTTP baseline probe. No baseline is recorded now.
2. On the developer machine, prepare the allowlist and local certificate materials; validate the certificate plan and provide the orders kit before changing behavior. Do not copy private keys into the repository.
3. Implement the Python TLS listener alongside legacy HTTP (`components/catalog/service.py:24-43`): TLS 1.2 minimum, catalog-only consumer CA, initially optional client certificates, per-request readiness access logging and fail-closed reloadable CN allowlisting. Preserve `/price/<sku>` and `/health` semantics. Confirm stage-2 health handling given the owner's no-management-port decision.
4. Change the separately deployed orders client (`components/orders/catalog_client.py:11-29`) to use the verified catalog CA and orders client certificate, an HTTPS-only configured `CATALOG_URL`, hostname verification and no HTTP retry. Preserve SKU quoting, 404 behavior and timeout semantics; evaluate handshake latency against the baseline. Direct in-process imports (`components/orders/orders.py:5,19-20,38-40`) are not network calls and should remain unchanged.
5. Adapt `components/orders/test_catalog_client.py:13-62` to TLS while retaining price, quantity, 404, quoting, query and decoding assertions. Add tests for TLS settings, wrong hostname, missing or untrusted certificates, listed and unlisted CNs, log-only mode, allowlist removal and unreadable allowlist; prove `/health` also requires the intended credentials.
6. Advance only after each producer stage's required evidence: certificate check; P1 and applicable health verification; observed allowed orders mTLS calls and no unexpected unlisted callers; enforce allowlist and prove refusal cases; require client certificates; close port 8001 only after readiness or valid named sign-off. Stage 3 remains an observation pause. Roll back each stage via the prior listener/configuration, never by disabling certificate or hostname verification. Closing HTTP requires coordination to reopen it before any consumer rollback to HTTP.

The `producer.stage: 0` manifest value means planning only, not a completed stage; the gate requires 1–6, so E0 is not ready. Record the actual migrator model before stage 1 for an independent later judge; its identity is not known here. Update the stage only when its work and evidence exist.

## Deferred checks

- E1 test-report check: **not run**. `unittest` has no JUnit XML reporter here; the owner says none is installed or will be installed. The planned report directories in the manifest do not imply reports exist.
- Tests, baseline, certificates, probes, readiness and gate: **not run**, deferred to the developer machine after plan confirmation.
- E12: Python settings cannot be read by the Spring-only configuration checker; its later result is at best `not run`, requiring manual verification. Do not claim a gate outcome.
