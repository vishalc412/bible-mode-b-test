# The consumer kit (producer runs)

Consumer teams don't need any AI tool. The producer run builds one kit per consumer:

```bash
<skill>/scripts/build-consumer-kit.sh --producer inventory --consumer orders --env test \
  --endpoint https://inventory.shop.svc.cluster.local:8443/stock/SKU-1 \
  --names inventory,inventory.shop.svc.cluster.local \
  --server-ca <server-ca.crt> --consumer-ca <inventory-consumers-ca.crt> \
  --out tls-migration/kits --cutover 2026-12-01 --contact "inventory team channel"
```

```text
kit-<producer>-for-<consumer>/
  README.md          plain steps for this kit's route, cutover date, contact
  endpoint.txt       URL, consumer id, producer, names, environment
  ca-bundle.pem      the producer's server CA (public): exactly one certificate (two during a server CA rotation: the new CA, then the old one)
  consumer-ca.crt    the CA that signs the consumer's own certificate (public)
  make-csr.sh        route A, one command (bash + OpenSSL 3 or 4); reads endpoint.txt
  _key_folder.sh     the key folder checks make-csr.sh sources (the same copy the toolkit uses)
  make-csr.ps1       the same for Windows PowerShell 7 (tested with Pester on pwsh 7.7)
  verify.sh          the handshake check; writes verify-result.json (no key material)
  snippets/          spring.yml, spring-pkcs12.yml, node.js, python.py, go.go, dotnet.cs, curl.sh
  KIT-MANIFEST.json  SHA-256 of every file, the route, the CA fingerprints, the kit fingerprint
  SHA256SUMS         one line per kit file except itself and KIT-MANIFEST.json: `<sha256>  <relative name>`, sorted
```

The endpoint is copied into shell and code snippets, so the script accepts only a plain `https://` URL: a host, an optional port, a simple path and query.

## Tamper check

The consumer runs the kit's scripts beside its own private key, so the whole kit is checked before anything in it runs, not only the CA.

**What the producer run sends.** `build-consumer-kit.sh` prints two values:

- the **kit fingerprint**: the SHA-256 of `SHA256SUMS`. `SHA256SUMS` lists the SHA-256 of every other file in the kit but `KIT-MANIFEST.json` (which records the fingerprint, so it cannot be listed), in the format `shasum -a 256 -c` reads, so this one value covers every file a consumer runs or trusts. It is also recorded in `KIT-MANIFEST.json` as `kit_fingerprint_sha256`;
- the **SHA-256 of `ca-bundle.pem`**, for `verify.sh` (below).

A person sends both values **over a different channel from the kit**: the ticket, chat or a call.

**The receiving team's first step,** before any script in the kit runs (the kit's README says the same):

1. Compute the SHA-256 of `SHA256SUMS` and compare it with the kit fingerprint received over the other channel. Different: stop, and ask the producer team for a new kit.
2. Check every file: `shasum -a 256 -c SHA256SUMS` (on Windows, `Get-FileHash -Algorithm SHA256` for each file, compared with its line). Any file that fails, or any file in the kit folder that `SHA256SUMS` does not list (other than `SHA256SUMS` and `KIT-MANIFEST.json`): stop.
3. Only then run `make-csr.sh` or `verify.sh`, each with `--kit-fingerprint <the kit fingerprint>`: they repeat both checks and refuse before touching any key on a mismatch. They cannot vouch for themselves, so steps 1 and 2 come first. On Windows, `.\make-csr.ps1 -KitFingerprint <the kit fingerprint>` does the same.

**`verify.sh`'s own check.** `verify.sh` runs only when `ca-bundle.pem` holds exactly one certificate and nothing else, **and** the value it is given equals either the SHA-256 of the whole file or that one certificate's own SHA-256 fingerprint (the script prints both). One certificate added to the bundle is therefore refused whichever value was sent. `--server-ca` must hold exactly one CA certificate. During a server CA rotation, `--previous-server-ca server-ca.previous.crt` adds the old CA after the new one; `verify.sh` then accepts exactly those two (both CAs, with the same name) and only the SHA-256 of the whole file ([certificates.md](certificates.md), "CA rotation"). `check.sh` (E9) checks `SHA256SUMS` and re-hashes every kit file against the manifest, and, because the manifest travels with the kit and can be re-written with it, also holds the kit against the toolkit and the plan: every file `build_kit.py` writes is there and nothing else, the toolkit's files are re-rendered from `kit-template` and compared, `endpoint.txt` sends consumers to an in-scope host, `consumer-ca.crt` is the plan's consumer CA, and `ca-bundle.pem` holds `CERTIFICATE` blocks only. A kit edited by hand, or built by an older toolkit, fails: rebuild it.

During a server CA rotation ([certificates.md](certificates.md), "CA rotation") the kit is rebuilt from the new CA alone (`server-ca.current.crt`), and the consumer trusts the old and the new kit's certificate together until the producer has switched.

## Route A (preferred)

1. The consumer runs `./make-csr.sh --kit-fingerprint <the kit fingerprint>` in the kit **where its key will live** and returns `<producer>-<consumer>.csr`. For staging and production it stops unless input is a terminal and the person types the environment name; `make-csr.ps1` does the same. An assistant never runs it for those environments: it writes the command into `tls-migration/requests/<name>.md` for the owners and pauses the item.
2. The producer run signs it:
   - local and test: `sign-csr.sh ... --out tls-migration/signed/<consumer> --name client.crt`, one folder per consumer so one consumer's file never overwrites another's;
   - staging and production: the signing ticket, Vault or cert-manager.
3. The certificate goes back to the consumer, who saves it as `client.crt` in the kit folder. The key never moves.

**Renewal.** The consumer runs `./make-csr.sh --renew` and returns the new `.csr`. Sign it with `--name client.crt.next` (same per-consumer folder). The consumer saves it as **`client.crt.next`**, never over `client.crt`, which the service is still using, then runs `./make-csr.sh --activate --cert client.crt.next`: that swaps key and certificate together and keeps the old pair as `.previous`. `--activate` refuses a `--cert` that is the file in use.

## Route B (fallback)

Use route B only when the policy sets `consumer_fallback_bundle: allowed` for the environment (or `allowed-with-signoff`, with the sign-off recorded). The script issues bundles in local and test only; in staging and production a bundle comes from the real issuer, by ticket.

1. `issue-client-bundle.sh --env <env> --producer <p> --consumer <id> --allowlist <file> --out <dir>` makes a 30-day PKCS12 file (AES-256): the consumer's key, its certificate and the consumer CA.
2. The script writes the password to a file under `$TLS_PRIVATE_DIR/bundles-<env>/`. You never open it; a person sends it over another channel.
3. `--out` must be outside every repository: the bundle holds a key. An existing folder is used as it is.
4. Build the kit with `--bundle <path to the .p12>`. The bundle is **not** copied into the kit: the manifest records its SHA-256, route B and `key_travelled: true`. A person delivers the bundle and its password over two other channels. `check.sh` (E9, E4) fails any key or key store found in a kit or the tree.
5. The kit's README then carries the route B steps: where to keep the bundle, `snippets/spring-pkcs12.yml`, and `./verify.sh --p12 <bundle> --p12-password-file <file>`.
6. The report lists the consumer under "Key travelled". The next renewal moves the consumer to route A.

## What every kit holds

- `ca-bundle.pem`: the server CA, the only CA the consumer trusts for this producer.
- `consumer-ca.crt`: the CA that signs the consumer's own certificate. Public. The consumer's `cert-check.sh` plan uses it as `issuer_ca` for the client certificate, so a consumer-only run can check its chain.
- `verify.sh`: first the client certificate is checked, before anything is sent: its CN is the kit's `consumer=`, it chains to `consumer-ca.crt` for client use, it has not expired, and the key belongs to it (each result is in `verify-result.json`; any failure exits non-zero with nothing sent). Then one mutual TLS call, marked with a fresh random 8-character tag in the header `X-TLS-Migration-Probe` (written to `verify-result.json` as `probe_tag`) so it never counts as the consumer having moved. Then P8: the same handshake, with `openssl`, expecting a wrong name must fail with a host name mismatch; no other failure counts. `verify-result.json` records the client certificate's SHA-256 and `openssl_wrong_name_refused` (also as `wrong_name_refused`, the name `check.sh` reads); `check.sh` binds both to the consumer's certificate plan.

  P8 is run with `openssl` on the consumer's machine. It shows the endpoint and CA behave for a client that checks names; it does not test the consumer's own code. That is what the consumer's test is for ([consumer.md](consumer.md), step 8) and what E3 scans for.

For staging and production, the consumer's certificates come from the platform. Ask the platform owners for the public certificate file (or read the chain the endpoint presents, as in [consumer.md](consumer.md)), and save it for the plan, for example as `tls-migration/evidence/orders-client.crt`. Never query a Secret object yourself: it holds the private key too.
