# Apigee as the gateway

Read [gateway.md](gateway.md) first. This file adds what is specific to Apigee.

Checked against Google's Apigee documentation on 2026-11-11. Items marked **not verified** were not found on the pages read; confirm them in the current documentation before relying on them. Nothing here has been run against a real Apigee installation.

## Contents

- First, find out which Apigee
- Connection 2: Apigee to the back end
- Keystores, truststores and references
- Connection 1: the caller to Apigee
- What the assistant produces
- Order for a route through Apigee

## First, find out which Apigee

| Product | Where it runs | Caller-side TLS is configured in |
| --- | --- | --- |
| Apigee hybrid | Runtime in the customer's Kubernetes clusters | The `virtualhosts` section of the hybrid overrides file |
| Apigee Edge (including the on-premises edition) | Google-hosted or the customer's own servers | Virtual hosts, with keystores and truststores |
| Apigee X | Google Cloud | **Not verified.** Not covered by the pages read. |

Record the product and version in the inventory. Do not guess: the caller-side steps differ.

Apigee ends TLS and opens a new connection to the back end. Pass-through was not described on the pages read (**not verified** as unsupported), so plan two connections.

## Connection 2: Apigee to the back end

This is configured per API proxy, in the target endpoint, or in a shared target server definition. If both carry TLS settings, the target server's take precedence (stated for Edge).

Mutual TLS to the back end:

```xml
<TargetEndpoint name="default">
  <HTTPTargetConnection>
    <URL>https://inventory.example.internal:8443</URL>
    <SSLInfo>
      <Enabled>true</Enabled>
      <Enforce>true</Enforce>
      <ClientAuthEnabled>true</ClientAuthEnabled>
      <KeyStore>ref://backendKeystoreRef</KeyStore>
      <KeyAlias>gateway-client</KeyAlias>
      <TrustStore>ref://backendTruststoreRef</TrustStore>
    </SSLInfo>
  </HTTPTargetConnection>
</TargetEndpoint>
```

| Element | Meaning | Default |
| --- | --- | --- |
| `Enabled` | Use TLS with the settings in this block | `false` |
| `Enforce` | Strict validation of the back end's certificate: fails on invalid, expired, self-signed, wrong host name or untrusted root | `false` |
| `ClientAuthEnabled` | Apigee presents a client certificate (mutual TLS) | `false` |
| `KeyStore`, `KeyAlias` | The keystore and entry holding Apigee's client certificate and key. `KeyAlias` is required when `ClientAuthEnabled` is true. | |
| `TrustStore` | The keystore of certificates Apigee trusts for this back end | |
| `IgnoreValidationErrors` | Ignore validation errors. Has no effect when `Enforce` is true. | `false` |
| `CommonName` | A name Apigee checks against the back end certificate's common name or alternative names | |
| `Protocols`, `Ciphers` | Restrict TLS versions and ciphers | |

**The trap.** Changing the URL to `https://` and setting `Enabled` is not enough. By default Apigee does not validate the back end's certificate, and `Enforce` defaults to `false`. A migration that stops there has encrypted the connection without verifying who is at the other end. Always set a `TrustStore`, switch strict validation on, and never set `IgnoreValidationErrors` to `true`.

Which element switches strict validation on depends on the product and version: check the `SSLInfo` reference for **your** Apigee (Edge, hybrid or X) before writing the block. Where `<Enforce>` is listed, set it to `true`; where it is not, the page will name what validates the host name (a `TrustStore` with `<CommonName>`, for example). Record the page and its date in the request. Then prove it: a back end presenting a wrong certificate must be refused (step 3 of the order below).

Search existing proxies and target servers for `IgnoreValidationErrors`, for `SSLInfo` blocks without `Enforce` or `TrustStore`, and for target URLs still on `http://`. Each is a finding.

Client certificates used for mutual TLS must carry the client-authentication usage. Google's reference warns that Apigee requires it, on both connections.

## Keystores, truststores and references

- A **keystore** holds a certificate and its private key under an alias. A **truststore** holds trusted certificates only; never upload a private key into one. On Edge a truststore is a keystore object used as a truststore.
- They are created through the Apigee management interface or API. References are scoped to an environment. Keystore scope was **not verified**.
- An existing keystore or truststore cannot be updated with a new certificate. To rotate: create a new keystore or truststore under a new name (keeping the alias name), then point the **reference** at it. This is why the configuration above uses `ref://` names and not keystore names: rotation then needs no proxy redeployment.
- On Edge, the owner is responsible for updating the truststore before a certificate expires.

The private key for Apigee's client certificate is uploaded into Apigee's keystore by Apigee's owners. The assistant never handles it. Under every policy mode, the assistant's part is the request: which certificate, which names and usage, which keystore, alias and reference it belongs in.

## Connection 1: the caller to Apigee

**Hybrid**, in the overrides file under `virtualhosts`:

- One-way TLS: `name` with `sslCertPath` and `sslKeyPath`, or `name` with `tlsMode: SIMPLE` and `sslSecret`.
- Mutual TLS: `tlsMode: MUTUAL` with `caCertPath`, `sslCertPath` and `sslKeyPath`; or `tlsMode: MUTUAL` with `sslSecret` and a separate secret for the trusted authority named `<secret name>-cacert`, holding a key called `cacert`.

**Edge**: a virtual host with a host alias, port, keystore and key alias, and a truststore when callers must present certificates. The exact property names were **not verified**.

**Apigee X**: **not verified**.

How a proxy can read the caller's certificate details (for passing the caller's identity on to the back end) was **not verified**. If the receiver needs the caller's identity, raise it as an open item.

The caller itself is changed as in [consumer.md](consumer.md): the Apigee host's HTTPS address, trust for the authority that issued Apigee's certificate, host name checking on, and a client certificate when the target is mutual.

## What the assistant produces

Following the policy file's `gateway_changes`:

- **`prepare-request`** (the default): `tls-migration/requests/gateway-change.md`, with for each route:
  1. The proxy and target endpoint or target server affected.
  2. The exact `SSLInfo` block to apply, as above.
  3. The keystore, alias, truststore and reference names needed, which exist and which are missing, and the certificate request for each missing one.
  4. The virtual host change for connection 1.
  5. How to verify each connection separately, and how to roll back.
- **`agent-may-edit`**: only where the proxy bundles or target server definitions are files in a repository in scope. The assistant edits those files as a separate change. It still does not create keystores or upload keys; those stay a request.

## Order for a route through Apigee

1. The back end accepts TLS beside plain HTTP.
2. Truststore and reference for the back end's issuer exist in Apigee.
3. The target switches to `https://` with `Enabled` and `Enforce` true and the `TrustStore` set. Verify a call succeeds, and that a back end with a wrong certificate is refused.
4. Apigee's client keystore exists; `ClientAuthEnabled` is set; then the back end starts requiring a client certificate.
5. The virtual host serves TLS; callers switch to the HTTPS address; then mutual TLS for callers if required.
6. Plain HTTP is closed on the back end and on the virtual host.
