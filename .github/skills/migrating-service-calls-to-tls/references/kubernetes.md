# Kubernetes

Contents: certificates through a certificate controller (`platform-issues`) · mounting · A consumer's Secret · deployment files to change · renewal · service mesh

You never run `kubectl`, `helm`, `vault` or a cloud command line against a test, staging or production cluster, issuer or secrets store. In the mode `platform-issues` you write the certificate resource or request file into the repository; a person or the pipeline applies it. On a local cluster, run `kubectl` only when the user has told you the context.

## Certificates through a certificate controller (`platform-issues`)

When the cluster runs cert-manager, a certificate resource asks the approved issuer for a certificate. The controller generates the key inside a secret; nobody handles it. You write the resource; a person or the pipeline applies it.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: inventory-server
spec:
  secretName: inventory-server-tls
  duration: 2160h          # 90 days: the policy's server_lifetime_days
  renewBefore: 720h        # 30 days: more than the policy's renew_before_days (21), or cert-check.sh fails before each renewal
  privateKey:
    algorithm: ECDSA       # the policy's key_algorithm; RSA 2048 only where a runtime needs it
    size: 256
    encoding: PKCS8
    rotationPolicy: Always
  usages: [digital signature, server auth]
  dnsNames:
    - inventory
    - inventory.<namespace>.svc
    - inventory.<namespace>.svc.cluster.local
  issuerRef:
    name: <approved issuer>
    kind: ClusterIssuer   # or Issuer
```

- List every name callers use. Read the callers' configured addresses.
- A caller's certificate uses `usages: [digital signature, client auth]` and a `commonName` naming the caller (its consumer id). Its `issuerRef` is **the producer's own consumer issuer** (one per producer: [certificates.md](certificates.md)), never the issuer of the server certificates: the producer trusts that one CA and nothing else.
- The resulting secret holds `tls.crt`, `tls.key` and, for most issuers, `ca.crt`. `ca.crt` is the CA that signed **that** certificate. A producer may use the `ca.crt` of nothing but its consumer issuer for client trust. A consumer must not use its own Secret's `ca.crt` to trust the producer: it is the consumer CA, not the server CA. The consumer's trust is `ca-bundle.pem` from the kit, mounted from a ConfigMap (it is public).
- Use only the issuer named in the operator's policy file. Ask the platform owners which issuers exist; do not query the cluster. If the cluster has no certificate controller, this mode is not available: use `request-only`.

## Mounting

```yaml
volumeMounts:
  - name: tls
    mountPath: /etc/tls
    readOnly: true
volumes:
  - name: tls
    projected:
      sources:
        - secret:
            name: inventory-server-tls           # tls.crt, tls.key, ca.crt
        - configMap:
            name: inventory-consumers-ca         # the producer's consumer CA (public)
            items:
              - { key: inventory-consumers-ca.crt, path: consumers-ca.crt }
```

The server Secret does not hold the producer's consumer CA, the trust file its Spring config reads as `consumers-ca.crt` ([java-spring.md](java-spring.md)). Put `<producer>-consumers-ca.crt` (from `certgen-test-ca.sh`, or the company issuer's consumer CA) in a ConfigMap, or as a key of a Secret, and mount it under that exact name beside the Secret's files, as above.

**Never point the producer's client-certificate trust at the server Secret's `ca.crt`.** That is the server CA, the issuer of the server certificate, not the consumer CA.

Never put a key, or a certificate together with its key, in a config map, an environment variable or the image. A CA certificate alone is public and may sit in a ConfigMap.

## A consumer's Secret

A `kubernetes.io/tls` Secret always names its files `tls.crt` and `tls.key`. A consumer whose configuration reads `client.crt`, `client.key` and `ca-bundle.pem` maps them in the volume (or reads `tls.crt` and `tls.key` instead):

```yaml
volumes:
  - name: inventory-client
    projected:
      sources:
        - secret:
            name: orders-inventory-client        # kubernetes.io/tls
            items:
              - { key: tls.crt, path: client.crt }
              - { key: tls.key, path: client.key }
        - configMap:
            name: inventory-server-ca            # ca-bundle.pem from the kit
            items:
              - { key: ca-bundle.pem, path: ca-bundle.pem }
```

Without the mapping the files are not where the service looks, and it fails at start-up.

## Deployment files to change

| Item | Change |
| --- | --- |
| Config maps and environment values holding addresses | `https://`, with the TLS port |
| Container and service ports | The TLS port; remove the plain port at stage 6 |
| Readiness and liveness probes | Point at the management port, or set `scheme: HTTPS` when the receiver does not require a client certificate |
| Ingress or gateway routes | Per the gateway reference |
| Network policies | Allow the new port, then remove the old one |

## Renewal

A renewed certificate updates the secret, and the mounted files follow after a short delay. A producer's embedded server reloads them when its bundle says so ([java-spring.md](java-spring.md)). A consumer's HTTP client does not: restart the consumer's pods after its client certificate is renewed (a rollout, or a reloader that restarts pods when the Secret changes). Do not mount with `subPath`: such mounts never update.

## Service mesh

If the cluster's mesh already provides mutual TLS between pods, say so in the inventory and ask whether application-level TLS is still wanted. Do not layer both without a decision.
