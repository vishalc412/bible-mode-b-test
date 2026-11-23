# Local development: signing on the laptop

Producer and consumers run on one laptop (processes, docker-compose, kind or minikube) to test the change end to end before any shared environment is touched. Here the scripts act as the CA. No policy file is needed: the local rules are built in.

**Who starts what.** You run the toolkit's scripts. You do not start services, containers or clusters yourself: give the user the command, bound to 127.0.0.1, and wait until they say it is running. Never run `kubectl` unless the user has told you the context and it is a local cluster.

## One command

```bash
<skill>/scripts/local-tls-up.sh --repo . --producer inventory \
  --allowlist tls-migration/allowed-consumers.yaml \
  --names "localhost,127.0.0.1,::1,inventory,host.docker.internal"
export TLS_PRIVATE_DIR="$(cat tls-migration/local/private-dir.txt)"
```

It creates or reuses:

- `local-dev-server-ca`, `local-dev-<producer>-consumers-ca` and `local-dev-negative-test-untrusted-client`;
- the server certificate;
- a key and signed client certificate for every consumer in the allowlist;
- the refusal-probe certificates.

It writes:

- the public certificates to `tls-migration/local/certs/`: `server-ca.crt`, `<producer>-consumers-ca.crt`, `<producer>-server.crt` and `<producer>-<consumer>.crt`;
- the CA fingerprints to `tls-migration/local/ca-fingerprints.txt`;
- the plan for `cert-check.sh` to `tls-migration/local/certs-to-check.yaml`;
- the key folder's path to `tls-migration/local/private-dir.txt`. Every later command needs that folder: the `export` line above sets it for your shell. Tell the user where the key folder is before the first run.

A folder recorded in `private-dir.txt` is used only when it equals the exported `TLS_PRIVATE_DIR`, or is under `~/.tls-migration/private/` with the toolkit's mark for this repository. Any other recorded folder is ignored, with a note: a file in the repository never decides where keys go.

**Paths in the probe plan and the manifest** are inside the repository. Keys may be written `$TLS_PRIVATE_DIR/...`, or as an absolute path under the exported `TLS_PRIVATE_DIR`. Any other path fails E0, or the plan is refused.

The keys are in `$TLS_PRIVATE_DIR/local/<producer>/server.key`, `$TLS_PRIVATE_DIR/local/<producer>/<consumer>/client.key` and `$TLS_PRIVATE_DIR/probe-local/<producer>/`.

It also adds `tls-migration/local/` to `.gitignore`. It is safe to run again: whatever the current CA did not sign, or no longer matches its key, is re-issued. Run it once per producer; each run adds that producer's entries to the plan.

## What stays the same as everywhere else

- **Keys are handled by scripts only.** They live in `$TLS_PRIVATE_DIR`, outside the repository, and you don't open them. The script refuses a key folder inside the repository. When something fails, `cert-check.sh` explains it from the certificates.
- **Verification stays on.** Services point at the local CA file in a local-only config, such as `application-local.yml` or `docker-compose.yml`, never at trust-all.

## Containers

- The public files are world-readable, so a container can mount `tls-migration/local/certs/` read-only.
- The key folder is readable by you alone. Mount **only the key each container needs**, read-only, and run the container as your own user (docker-compose: `user: "${UID}:${GID}"`):
  - the producer: the one file `$TLS_PRIVATE_DIR/local/<producer>/server.key`;
  - each consumer: its own folder `$TLS_PRIVATE_DIR/local/<producer>/<consumer>/`.

  Never mount `$TLS_PRIVATE_DIR/local/<producer>` whole: it holds every consumer's key too, and the producer must never hold a key that lets it pass as a consumer. Never loosen a key's mode, and never copy a key into the repository or an image.
- kind or minikube: the person at the laptop creates the Secret from the key file by path (`kubectl create secret tls ... --key "$TLS_PRIVATE_DIR/local/<producer>/server.key"`). You give them the command; you don't run it on a key yourself.

## Guards that keep local certificates on the laptop

1. Never installed in the system, a browser or the JVM.
2. Every local CA name starts with `local-dev-`, and its fingerprint is recorded.
3. `check.sh` E10 fails any `local-dev-` name or recorded fingerprint outside these local-only files (build output and jars included, whatever label the certificate is written under):
   - `tls-migration/local/`;
   - `application-local.*`;
   - compose files whose name marks them local: `docker-compose*.local*.yml` and `compose.local*.yml` (any other compose file may deploy a shared environment);
   - `.env.local`.

   `cert-check.sh` fails a test, staging or production certificate that chains to one.
4. The CAs live 90 days and the leaf certificates 30. To remove every local key and certificate:

   ```bash
   <skill>/scripts/local-tls-up.sh --clean --repo .
   ```

   Ask the user before you run it: it deletes keys. It uses only the key folder recorded for that repository (`tls-migration/local/private-dir.txt`), and only when that folder is verified: it equals an exported `TLS_PRIVATE_DIR`, or lies under `~/.tls-migration/private/` and carries the toolkit's marker for this repository. `--clean` deletes only in such a folder, never through a symbolic link, removes the local environment only, and fails if it found no key there. Route B bundles written outside the key folder are listed, not removed: a person deletes them. The fingerprint list stays, so a leaked local CA is still recognised.

   One key folder per repository: when a `TLS_PRIVATE_DIR` exported for another repository is still set, `local-tls-up.sh` stops instead of reusing that repository's CAs and replacing its consumers' keys (both keep a key folder id: `tls-migration/local/key-folder-id.txt` and `$TLS_PRIVATE_DIR/local/key-folder-id.txt`). Unset it, or pass `--force` to share a folder on purpose.

## A repository that only calls the producer

A consumer-only repository has no producer to start. Locally it can reach `pass` in two ways:
- the producer team sends its local or test kit; the user runs `./verify.sh` from it, which writes the `verify-result.json` E6 reads;
- the endpoint asks for no client certificate: prove it with `probe-tls.sh --repo . --server-only <host:port>` (a `client_certificate: none` row, [analyse-and-plan.md](analyse-and-plan.md)).

Without either, the result stays `not proven`. Do not sign a stand-in producer yourself and report its result as proof of the real one.

## What local evidence proves

The code, config and stages work end to end. Probes run against `localhost`. Readiness needs each consumer seen once on mutual TLS. `check.sh` labels a passing result "proven locally with local-dev certificates", which never stands in for staging or production.
