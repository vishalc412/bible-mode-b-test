# Go

Contents: producer · consumer · files and local · never do this · tests

The gate's E12 reads Spring Boot configuration only. For this stack E12 reports `not run: stack not read (<stack>)`, so the overall result is at best `not proven` until a person or the judge checks these settings.

Written for the standard `net/http` and `crypto/tls` packages (Go 1.21 and later). Routers such as chi, gin or echo sit on the same `http.Server`. Record the Go version from `go.mod` first.

## Producer

Stage settings come from the environment. Suggested names, used the same way on every stack page: `TLS_CLIENT_AUTH` (`want` stages 2-4, `need` from stage 5), `TLS_LEGACY_HTTP_ENABLED` (`true` stages 2-5, `false` stage 6), `TLS_ALLOWLIST` (file path), `TLS_ALLOWLIST_ENFORCE` (`false` stages 2-3, `true` from stage 4).

```go
dir, keyDir := os.Getenv("TLS_DIR"), os.Getenv("TLS_KEY_DIR") // check both are set; fail at start-up if not
caPEM, err := os.ReadFile(dir + "/consumers-ca.crt")         // this producer's consumer CA only
if err != nil { log.Fatal(err) }
consumers := x509.NewCertPool()
if !consumers.AppendCertsFromPEM(caPEM) { log.Fatal("no CA certificate in consumers-ca.crt") }
mode := tls.VerifyClientCertIfGiven                            // stages 2-4: asks; checks a certificate when one is sent
if os.Getenv("TLS_CLIENT_AUTH") == "need" { mode = tls.RequireAndVerifyClientCert }
srv := &http.Server{Addr: ":8443", Handler: allowlist(mux), TLSConfig: &tls.Config{
	MinVersion: tls.VersionTLS12, ClientCAs: consumers, ClientAuth: mode,
}}
log.Fatal(srv.ListenAndServeTLS(dir+"/tls.crt", keyDir+"/tls.key"))
```

- **Allowlist and access line,** in one handler wrapped around the router: the CN is `r.TLS.PeerCertificates[0].Subject.CommonName` when `r.TLS != nil` and the slice is not empty; check it against the allowlist file (re-read when it changes; an unreadable file allows nobody); write the access line from [producer.md](producer.md), `probe=<id>` from the `X-TLS-Migration-Probe` header only when it matches `[A-Za-z0-9]{1,8}`, else `-`; answer 403 for an unlisted CN when enforcing.
- **Plain HTTP (stages 2-5):** a second `http.Server` without TLS on the old port, started only when `TLS_LEGACY_HTTP_ENABLED` is `true`; at stage 6 written out as `false`.
- **Health:** a separate plain `http.Server` on the management port, bound to the node network.
- **Renewal:** `tls.Config.GetCertificate` can load a renewed certificate without a restart; otherwise restart after each renewal and say so in the report.
- Tests (`httptest.NewUnstartedServer` with this `TLSConfig`, then `StartTLS`): listed consumer served; unlisted gets 403; log-only mode serves; a removed line cuts the consumer off; a missing allowlist file allows nobody.

## Consumer

```go
cert, err := tls.LoadX509KeyPair(dir+"/client.crt", keyDir+"/client.key")
if err != nil { log.Fatal(err) }
caPEM, err := os.ReadFile(dir + "/ca-bundle.pem")
if err != nil { log.Fatal(err) }
roots := x509.NewCertPool()                                    // the producer's CA only, not the system pool
if !roots.AppendCertsFromPEM(caPEM) { log.Fatal("no CA certificate in ca-bundle.pem") }
client := &http.Client{Timeout: 10 * time.Second, Transport: &http.Transport{TLSClientConfig: &tls.Config{
	Certificates: []tls.Certificate{cert}, RootCAs: roots, MinVersion: tls.VersionTLS12,
}}}
base := os.Getenv("INVENTORY_BASE_URL")
if !strings.HasPrefix(base, "https://") { log.Fatal("INVENTORY_BASE_URL must be set to an https:// URL") }
```

- Build the client once and share it. `http.DefaultClient` and `http.Get` do not carry this configuration.
- Host name checking is on whenever `InsecureSkipVerify` is unset. Leave it unset.
- A client reads its certificate once: restart after a renewal, or load it through `tls.Config.GetClientCertificate`.
- Tests: the client is built from these files; a blank or `http://` address is refused; a server certificate for another name is refused.

## Files and local

- Paths come from the environment (`TLS_DIR`, `TLS_KEY_DIR`). Keys never live in the repository and are never committed; never `embed` one.
- Local: certificates from `tls-migration/local/certs/` (`<producer>-server.crt`, `<producer>-consumers-ca.crt`, `server-ca.crt` as the consumer's `ca-bundle.pem`, `<producer>-<consumer>.crt`); keys `$TLS_PRIVATE_DIR/local/<producer>/server.key` and `$TLS_PRIVATE_DIR/local/<producer>/<consumer>/client.key`. Put these paths only in local-only files (`.env.local`, `docker-compose.local.yml`): E10 fails `local-dev-` references anywhere else.
- A call that must stay on plain HTTP gets exactly `// TODO: HTTPS not supported - requires infrastructure update` beside it ([analyse-and-plan.md](analyse-and-plan.md)).

## Never do this

None of these may appear, not even in tests. The gate's scanner looks for most of them; a person or the judge checks the rest:

- `InsecureSkipVerify: true`, or `InsecureSkipVerify:` set from a variable or flag;
- a `VerifyPeerCertificate` or `VerifyConnection` callback that replaces the normal checks;
- `MinVersion: tls.VersionTLS10` or `tls.VersionTLS11`;
- on a producer from stage 5: `ClientAuth` of `tls.NoClientCert`, `tls.RequestClientCert` or `tls.RequireAnyClientCert` (the last two accept a certificate without checking it);
- `curl -k` / `--insecure` in scripts.

## Tests and JUnit XML

E1 reads JUnit-style XML only, and `go test` does not write it. Write it to `<service>/build/test-results/` and list that folder under `evidence.tests` in the manifest. Both converters below are extra tools a person must approve and add if the project does not already have them; you never install them.

- gotestsum: `gotestsum --junitfile build/test-results/go-test.xml -- ./...`.
- go-junit-report: `go test -v ./... 2>&1 | go-junit-report -set-exit-code > build/test-results/go-test.xml` (`-set-exit-code` keeps a failing run failing; check the version you use).
