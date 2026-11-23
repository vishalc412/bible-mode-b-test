# Certificates: what each side gets, and who makes the key

Contents: certificate set per side · one consumer CA per producer · modes · where a key is made · the scripts · CA rotation · probe certificates · certificate plan · never

## Certificate set per side

| Side | Presents | Trusts | Usage | Names |
| --- | --- | --- | --- | --- |
| Producer | a server certificate | only its own consumer CA, plus the name allowlist | `serverAuth` only | every name a consumer uses: config, code fallbacks, deploy files, the kit. IP addresses only if a consumer really dials one. |
| Consumer | a client certificate | only the issuer of the producer it calls; the system store for public-CA third parties only | `clientAuth` only | `CN=<consumer id>`, plus `URI:spiffe://<trust-domain>/consumer/<id>` |
| Both (a gateway) | two separate certificates | both of the above | one usage each | separate certificates, so one stolen key can't act in both directions |

Every certificate has:

- `CA:FALSE`;
- `digitalSignature`;
- a lifetime within the policy, and never past its CA's own end date;
- an EC P-256 key, or RSA 2048 where a runtime needs it.

## One consumer CA per producer

A certificate issued for producer A's consumers gets nowhere at producer B, even under the same company root.

| Environment | Consumer CA |
| --- | --- |
| local | `local-dev-<producer>-consumers-ca`, made by `certgen-test-ca.sh` on the laptop ([local.md](local.md)); lives 90 days |
| test | `test-<producer>-consumers-ca`, made by `certgen-test-ca.sh` (lives 180 days) or by an in-cluster cert-manager `Issuer` |
| staging, production | an intermediate under the company CA, constrained as tightly as the issuer allows (see below). Signing happens in the issuer, never on a workstation. |

The constraints for staging and production:

- `pathlen:0`;
- extended key usage `clientAuth` only;
- in Vault: a role with `client_flag=true`, `server_flag=false` and `allowed_domains` set to the consumer ids.

## Modes

`local` is built in: `test-certificates`, signed on this machine. In every other environment the operator's policy file, kept outside the repository, lists the modes allowed; you ask the user which one to use. The shipped example allows only `request-only` in staging and production.

| Mode | Server certificate | Consumer certificate | Who holds keys |
| --- | --- | --- | --- |
| `test-certificates` (local, test) | `make-server-cert.sh` signs with the test or local CA | `make-csr.sh` on the consumer, then `sign-csr.sh` | the laptop or test environment |
| `platform-issues` | you write the certificate resource (a cert-manager `Certificate`, [kubernetes.md](kubernetes.md)) or the issuer's request file into the repository; a person or the pipeline applies it, and the key is made where it lives | the same, from the producer's consumer issuer, which issues client certificates only | the platform; you see certificates and fingerprints only |
| `request-only` | you write `tls-migration/requests/<name>.md`: the names, the usage and the exact `make-server-cert.sh --request-only --env <env>` command. The owners of the target run it there; it makes a new key and a CSR | the same, with the `make-csr.sh` command; the CSR goes to the signing ticket | the certificate owners |

`platform-issues` never means that you operate the platform. You never run `kubectl`, `helm`, `vault` or a cloud command line against a test, staging or production cluster, issuer or secrets store. It counts only when the operator's policy outside the repository lists it.

## Where a key is made

**A key is made where it will live.** No script moves a key, and you never copy one.

- **local:** on the laptop. The services read the keys straight from `$TLS_PRIVATE_DIR`.
- **test with the scripts' CA:** on the host, or in the pipeline job, that loads the test environment's secret store. A person (or that pipeline) puts the key into the Secret; you name the file and the Secret, nothing more.
- **staging and production:** you never run `make-server-cert.sh`, `make-csr.sh` or `make-probe-certs.sh` for these environments, on any machine. You write the exact command and the names into `tls-migration/requests/<name>.md` for the owners of the target, and pause that item. They run it **on the target host or in the deployment pipeline**. For these environments `make-server-cert.sh --request-only`, `make-csr.sh` and `make-probe-certs.sh --request-only` stop unless input is a terminal and the person types the environment name when asked, so a key is never made there without a person present. The kit's `make-csr.ps1` does the same.
- **Where cert-manager or Vault makes the key in place,** that is better still: no person makes a key at all. That is the mode `platform-issues`, when the operator's policy lists it.

## The scripts

All scripts are in `scripts/`. All of them:

- need OpenSSL 3 or later; 3 and 4 both work (LibreSSL, the `openssl` of stock macOS, is refused). When it is missing, stop and ask the person at this machine to install it; you never install software;
- run with `umask 077`;
- write keys only under `$TLS_PRIVATE_DIR`, and refuse a folder inside a repository (a `.git`, `.svn`, `.hg` or `tls-migration/` above it). The producer scripts have no default: set it per project (for example `~/.tls-migration/private/<project>`). `local-tls-up.sh` picks `~/.tls-migration/private/<repo>-<8 hex>` when it is unset, marks that folder as belonging to this repository, and records it in `tls-migration/local/private-dir.txt`; for later commands run `export TLS_PRIVATE_DIR="$(cat tls-migration/local/private-dir.txt)"`. A recorded folder is honoured only when it equals an exported `TLS_PRIVATE_DIR`, or lies under `~/.tls-migration/private/` and carries the toolkit's marker for this repository: a file in the repository cannot send keys elsewhere. Tell the user the key folder before the first key is made. Only the kit's `make-csr.sh`, on the consumer's machine, defaults to `~/.tls-migration/private`;
- keep every environment apart, keys as well as CAs:

  ```text
  $TLS_PRIVATE_DIR/ca-<env>/                               CAs (local, test)
  $TLS_PRIVATE_DIR/<env>/<service>/server.key              a server key
  $TLS_PRIVATE_DIR/<env>/<producer>/<consumer>/client.key  a consumer's key for one producer
  $TLS_PRIVATE_DIR/probe-<env>/<producer>/                 probe certificates
  $TLS_PRIVATE_DIR/bundles-<env>/                          route B work files
  ```

- build a new key and certificate beside the pair in use and swap both only when signing worked; a failure prints openssl's own message and changes nothing;
- reuse a certificate only when it was signed by that environment's current CA and matches its key;
- print only public metadata: subject, issuer, names, usage, expiry and SHA-256.

| Script | Does |
| --- | --- |
| `certgen-test-ca.sh --env local\|test --producer <p> --out <dir>` | server CA, consumer CA, negative-test CA; reused while more than 45 days (local) or 60 days (test) are left, then rotated (below) |
| `certgen-test-ca.sh --clean --env <env> [--out <dir>]` | removes that environment's CAs, keys (also those kept as `.previous`, `.next` or a `.new` left by an interrupted run), probe certificates and the recorded route B bundles inside the key folder (bundles written outside it are listed, not removed), and nothing of another environment. Fails when it finds no key: then `TLS_PRIVATE_DIR` is the wrong folder |
| `make-server-cert.sh --env <e> --service <p> --names <list> --out <dir> [--renew-before N \| --policy <file>] [--after-overlap]` | the server certificate (leaf, then the CA). Names are checked: no ports, a wildcard only as `*.two.labels`. Re-issued when N days or fewer are left (default the policy's `renew_before_days`, else 21, the value `cert-check.sh` applies). During a server CA rotation it keeps the leaf the previous CA signed until `--after-overlap`, and stops (exit 1, nothing changed) when that leaf can no longer be kept |
| `make-server-cert.sh --request-only --env <e> ...` | a **new** key and a CSR for staging or production, run by the owners of the target at a terminal (it asks them to type the environment name); `--reuse-key` only for a request still waiting for its certificate |
| `make-csr.sh --consumer <id> --producer <p> [--env <e>] [--kit-fingerprint <hex>]` | the consumer's key and CSR, one key per producer; `--renew`, then `--activate --cert <file>` ([cutover.md](cutover.md)). With `--env staging` or `production` it asks the person at the terminal to type the environment name. In a kit, `--kit-fingerprint` checks `SHA256SUMS` before any key is touched |
| `sign-csr.sh --env <e> --producer <p> --csr <file> --allowlist <file> --out <dir> [--name client.crt]` | signs a consumer CSR; see below |
| `issue-client-bundle.sh` | route B: a PKCS12 bundle for a consumer who can't run a script ([consumer-kit.md](consumer-kit.md)) |
| `make-probe-certs.sh --env <e> --producer <p> [--allowlist <file>]` | the probe certificates (below); for staging and production, interactive as above |
| `cert-check.sh --repo . --plan <yaml> --out <json>` | checks every certificate and trust store against the plan |

`sign-csr.sh` treats the CSR as untrusted. It refuses a request that:

- has a bad self-signature;
- asks for `CA:TRUE`, extra names, or any usage other than client authentication;
- carries a subject with anything besides the CN;
- has a CN that isn't in `allowed-consumers.yaml`, or an allowlist whose `producer:` is not the `--producer` given;
- uses a weak key.

It also refuses every `tls-probe-*` CN, even one on the allowlist: only `make-probe-certs.sh` issues probe identities.

It then sets the subject, the usage, the URI name and the lifetime itself. It writes `<producer>-<consumer>.crt`; with `--name` it writes the file under the name the consumer's kit expects: `client.crt` for a first certificate, `client.crt.next` for a renewal (the file in use is swapped only by `make-csr.sh --activate`). Use one `--out` folder per consumer.

## CA rotation (local and test)

When a CA has 45 days or less left in local (90-day CAs), or 60 days or less in test (180-day CAs), the next `certgen-test-ca.sh` run makes a new one. That is early on purpose: the server certificate is re-issued at 21 days left (`--renew-before`, 7 in `local-tls-up.sh`), so the leaf the old CA signed can still be kept for an overlap of at least 24 days (39 in test). The old certificate is kept as `<name>.previous.crt` until it expires (its key is removed), and the trust file in `--out` holds **both**, new first, so certificates the old CA signed keep working during the overlap.

After a rotation:

1. **Consumer CA:** deploy the producer's two-CA trust file `<producer>-consumers-ca.crt`. Consumers renew at their own pace before the old CA expires; `sign-csr.sh` signs with the new CA.
2. **Server CA:** rebuild each kit with both CAs: `build-consumer-kit.sh ... --server-ca <out>/server-ca.current.crt --previous-server-ca <out>/server-ca.previous.crt`. Its `ca-bundle.pem` then holds exactly two certificates, the new CA and then the old one, both with the same name; that is the only two-certificate form `verify.sh` accepts, and only with the SHA-256 of the whole file. Send the kit and that SHA-256 as usual. Each consumer replaces its `ca-bundle.pem` with the new one (its trust file now holds both CAs), restarts, runs the rebuilt kit's `verify.sh` and sends back `verify-result.json`.
   - **Every consumer trusts both** when, for every consumer on the allowlist, you hold a `verify-result.json` from the rebuilt kit with `"ca_overlap": true`, `"ok": true`, and `ca_bundle_sha256` equal to the SHA-256 you sent, and the consumer has confirmed that every instance now runs with that `ca-bundle.pem`. Check that list against the allowlist; a consumer missing from it still trusts only the old CA.
   - Only then run `make-server-cert.sh --after-overlap` (`local-tls-up.sh --after-overlap` on a laptop): it re-issues the server certificate under the new CA. Until then `make-server-cert.sh` and `local-tls-up.sh` keep the leaf the previous CA signed (and refuse a change of names, which would need a new leaf), so no consumer is cut off early. When that leaf can no longer be kept (it has `--renew-before` days or fewer left, or its key is gone), they stop with exit 1 and change nothing; `--force` re-issues regardless.
   - Once the old CA has expired, rebuild the kits from `server-ca.crt` alone; consumers drop the old CA.
3. In `certs-to-check.yaml`, list the CA name **twice** in `expect_only` for every trust file that holds two.

`local-tls-up.sh` does all of this in one run on a laptop.

## Probe certificates

| File in `$TLS_PRIVATE_DIR/probe-<env>/<producer>/` | CN | Signed by | Proves |
| --- | --- | --- | --- |
| `probe-unlisted` | `tls-probe-unlisted` | the producer's consumer CA | P4: a valid certificate that is not on the allowlist gets 403. `sign-csr.sh` never signs this name |
| `probe-untrusted` | `tls-probe-untrusted` | a CA nothing trusts | P3: refused at the handshake |
| `probe-allowed` | `tls-probe-allowed` | the producer's consumer CA | P1 where the producer run holds no consumer's key: every environment but local |

- **local:** `local-tls-up.sh` makes them; P1 uses a real consumer's local certificate.
- **test:** add `- id: tls-probe-allowed` (owner: the producer team, `cadence: continuous`) to `allowed-consumers.yaml`, then `make-probe-certs.sh --env test --producer <p> --allowlist <file>`.
- **staging and production:** you write the command into `tls-migration/requests/probe-certs.md`; the owners of the probe location run it there, at a terminal: `make-probe-certs.sh --request-only --env <env> --producer <p> --out tls-migration/requests`. It makes the three keys there, signs `probe-untrusted` with a throwaway CA, and writes `probe-unlisted.csr` and `probe-allowed.csr` for the real consumer issuer. `tls-probe-allowed` goes on the allowlist; `tls-probe-unlisted` never does.

Never issue yourself a certificate for a real consumer's id to make a probe pass.

## Certificate plan for `cert-check.sh`

Write `tls-migration/certs-to-check.yaml` (local runs: `local-tls-up.sh` writes `tls-migration/local/certs-to-check.yaml`). Its format is in the header of `scripts/cert_check.py`.

Each trust store lists in `expect_only` the CA names it may hold, so a store wider than planned fails.

## Never

- Read, print or move a key yourself. When a key is in the wrong place, say where it is and what a person should do.
- Install any CA in the system, a browser or the JVM `cacerts`. Each service points at its CA file in its own config.
- Use a test or local CA outside its environment. `cert-check.sh` fails a `local-dev-` CA anywhere but local and a `test-` CA anywhere but test; `check.sh` (E5, E6, E10) fails them too, from the files and from the chain a live probe sees.
