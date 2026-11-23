# Connecting to {{PRODUCER}} over mutual TLS

This kit is for the **{{CONSUMER}}** service. It lets you call {{PRODUCER}} over HTTPS with your own client certificate. You don't need any AI tool.

| | |
| --- | --- |
| Endpoint | `{{ENDPOINT}}` |
| Environment | {{ENVIRONMENT}} |
| Names on the producer's certificate | {{NAMES}} |
| Your consumer id (the CN on your certificate) | `{{CONSUMER}}` |
| Plain HTTP closes on | {{CUTOVER}} |
| Contact | {{CONTACT}} |

You need bash, curl and **OpenSSL 3 or later** (3 and 4 both work). The `openssl` that ships with macOS is LibreSSL and is refused: install OpenSSL and put it first on your `PATH` before you start.

## 1. Check the kit, before you run anything in it

Ask the producer team for two values by chat, phone or ticket, **not by the channel that brought you this kit**: the **kit fingerprint** (the SHA-256 of `SHA256SUMS`) and the **SHA-256 of `ca-bundle.pem`**. Do this first, before any script in this folder runs:

1. Compare the kit fingerprint with `SHA256SUMS`: `shasum -a 256 SHA256SUMS` (Linux: `sha256sum SHA256SUMS`; PowerShell: `Get-FileHash SHA256SUMS -Algorithm SHA256`). It must be the value you were given. If it differs, stop and call the producer team.
2. Check every file of the kit against `SHA256SUMS`: `shasum -a 256 -c SHA256SUMS` (Linux: `sha256sum -c SHA256SUMS`). Every line must say `OK`. In PowerShell, compare `Get-FileHash <file> -Algorithm SHA256` with each line by hand.

`./verify.sh` and `./make-csr.sh` repeat both checks when you add `--kit-fingerprint <the kit fingerprint>`, and then refuse to touch any key in a kit that does not match. They cannot vouch for themselves, so the two steps above come first.

`verify.sh` also refuses to run unless the whole `ca-bundle.pem` matches the SHA-256 you were given for it. Compare it yourself too: `openssl dgst -sha256 ca-bundle.pem`.


`ca-bundle.pem` holds exactly one certificate. If the producer team later tells you its CA is being replaced, you will get a new kit, a new kit fingerprint and a new SHA-256: check the new kit as above first; its `ca-bundle.pem` holds two certificates, the new CA and then the old one. Put that file in place of the old one, restart, run `./verify.sh` and send back `verify-result.json` (it shows `"ca_overlap": true`). When the old CA has expired you get a kit with the new CA alone.
{{#ROUTE_A}}

## 2. Get your certificate (route A)

Run this **where the key will live**: on the machine, or in the pipeline, that loads your service's secret store. Not on a laptop the key would later have to leave.

```bash
./make-csr.sh --kit-fingerprint <the kit fingerprint>
```

For `staging` and `production` it asks you to type the environment's name before it makes the key, and stops when it is not run at a terminal: a person runs it, never an assistant or an unattended job.

This creates your private key in `$TLS_PRIVATE_DIR/{{KEY_SUBPATH}}/client.key` (`TLS_PRIVATE_DIR` defaults to `~/.tls-migration/private`) and writes `{{PRODUCER}}-{{CONSUMER}}.csr`. The key is for {{PRODUCER}} only; a kit from another producer makes its own.

Send **only the `.csr` file** to the producer team. They send back a certificate. Save it in this folder as **`client.crt`**.

Never send the key, never commit it, and never put it in an image. Windows: `./make-csr.sh` works under Git Bash; `.\make-csr.ps1 -KitFingerprint <the kit fingerprint>` does the same in PowerShell.

Where your platform makes keys itself (cert-manager, Vault), use that instead and skip `make-csr.sh`: ask for a client certificate with `CN={{CONSUMER}}` from the issuer the producer team names.
{{/ROUTE_A}}
{{#ROUTE_B}}

## 2. Your certificate (route B: a ready-made bundle)

The producer team made your key and certificate for you and sends them as one file, `{{PRODUCER}}-{{CONSUMER}}.p12`, **separately from this kit**. Its password arrives over a third channel. Because your key has travelled, this bundle lasts 30 days at most; the next one should use route A (`./make-csr.sh`, then send only the `.csr`).

- Keep the `.p12` and the password out of this folder, out of any repository and out of any image.
- Save the password in a file only you can read (`chmod 600`). Tools read it from that file; never type it on a command line.
- The bundle holds your key, your certificate and the CA that signed it. It does **not** hold the CA you must trust: that is `ca-bundle.pem` in this kit.
{{/ROUTE_B}}

## 3. Configure your client

Your client needs three things:

{{#ROUTE_A}}
- your certificate `client.crt`;
- your key;
{{/ROUTE_A}}
{{#ROUTE_B}}
- the bundle `{{PRODUCER}}-{{CONSUMER}}.p12` (your key and certificate);
- its password, from a secret;
{{/ROUTE_B}}
- `ca-bundle.pem` as the **only** CA it trusts for this endpoint.

Ready-made examples are in `snippets/` for Spring Boot ({{#ROUTE_A}}`spring.yml`{{/ROUTE_A}}{{#ROUTE_B}}`spring-pkcs12.yml`{{/ROUTE_B}}), Node, Python, Go, .NET and curl. Keep host name checking on, and never switch certificate checking off, not even to test.

Kubernetes: put the certificate and key in a `kubernetes.io/tls` Secret. Its files are always called `tls.crt` and `tls.key`; `snippets/spring.yml` shows the mapping to the names your config reads. Mount the folder, never a single file with `subPath`.

## 4. Prove it works

`verify.sh` needs bash. On Windows, run it under Git Bash or WSL. Before it sends anything it checks your certificate: its name must be your consumer id, it must come from `consumer-ca.crt`, it must not have expired, and your key must belong to it. If one of these fails it sends nothing and says which.

```bash
{{#ROUTE_A}}
./verify.sh --kit-fingerprint <the kit fingerprint> --expect-fingerprint <the SHA-256 of ca-bundle.pem>
{{/ROUTE_A}}
{{#ROUTE_B}}
./verify.sh --kit-fingerprint <the kit fingerprint> --expect-fingerprint <the SHA-256 of ca-bundle.pem> --p12 <path to the .p12> --p12-password-file <the password file>
{{/ROUTE_B}}
```

Send `verify-result.json` to the producer team. It holds no key material.

This proves you **can** connect. The check marks its request with a fresh random tag in `X-TLS-Migration-Probe` (recorded as `probe_tag` in `verify-result.json`), so it never counts as your service having moved: the producer counts you only when your service's real calls arrive with your certificate. Its last step (a wrong server name must be refused) is done with `openssl` on this machine; your own client must keep host name checking on, and your tests should show that.

## Renewal

Certificates last {{LIFETIME}} days. A running service does **not** pick up a new certificate by itself: plan a restart (or a secret update and rollout) for the end of these steps.
{{#ROUTE_A}}

1. Before yours expires, run `./make-csr.sh --renew` and send the new `.csr`. The new key waits in `client.key.next`; the key in use stays, so your service keeps working. Run it once: a second run is refused, because it would orphan the request you already sent.
2. When the new certificate arrives, save it in this folder as **`client.crt.next`**, never over `client.crt` (your service is still using it), and run `./make-csr.sh --activate --cert client.crt.next`. The script checks that the certificate belongs to the waiting key, then swaps key and certificate together (`client.crt` in this folder; the old pair is kept as `.previous`).
3. Update your service's secret from the new pair and restart it. Check with `./verify.sh`.

Windows: `.\make-csr.ps1 -Renew`, then `.\make-csr.ps1 -Activate -Cert <file>`.
{{/ROUTE_A}}
{{#ROUTE_B}}

Ask the producer team for a new bundle before this one expires, or better, move to route A: `./make-csr.sh`, then send only the `.csr`.
{{/ROUTE_B}}
