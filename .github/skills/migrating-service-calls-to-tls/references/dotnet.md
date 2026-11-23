# .NET (ASP.NET Core and HttpClient)

Contents: producer · consumer · files and local · never do this · tests

The gate's E12 reads Spring Boot configuration only. For this stack E12 reports `not run: stack not read (<stack>)`, so the overall result is at best `not proven` until a person or the judge checks these settings.

Written for .NET 8 and Kestrel. Record the target framework from the `.csproj` first; on .NET 9 and later, prefer `X509CertificateLoader` for loading a certificate-only file.

## Producer

Stage settings come from configuration (`appsettings.json` keys, overridable by environment variables). Suggested names, used the same way on every stack page: `TLS_CLIENT_AUTH` (`want` stages 2-4, `need` from stage 5), `TLS_LEGACY_HTTP_ENABLED` (`true` stages 2-5, `false` stage 6), `TLS_ALLOWLIST` (file path), `TLS_ALLOWLIST_ENFORCE` (`false` stages 2-3, `true` from stage 4).

```csharp
var dir = builder.Configuration["TLS_DIR"] ?? throw new InvalidOperationException("TLS_DIR is not set");
var keyDir = builder.Configuration["TLS_KEY_DIR"] ?? throw new InvalidOperationException("TLS_KEY_DIR is not set");
var consumersCa = new X509Certificate2($"{dir}/consumers-ca.crt");    // this producer's consumer CA only
var need = builder.Configuration["TLS_CLIENT_AUTH"] == "need";
builder.WebHost.ConfigureKestrel(k => k.ListenAnyIP(8443, listen => listen.UseHttps(https =>
{
    https.ServerCertificate = X509Certificate2.CreateFromPemFile($"{dir}/tls.crt", $"{keyDir}/tls.key");
    https.SslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13;
    https.ClientCertificateMode = need ? ClientCertificateMode.RequireCertificate
                                      : ClientCertificateMode.AllowCertificate;   // stages 2-4
    https.ClientCertificateValidation = (cert, _, _) =>
    {
        using var chain = new X509Chain();
        chain.ChainPolicy.TrustMode = X509ChainTrustMode.CustomRootTrust;    // the consumer CA, not the machine store
        chain.ChainPolicy.CustomTrustStore.Add(consumersCa);
        chain.ChainPolicy.RevocationMode = X509RevocationMode.NoCheck;       // as in the kit snippet; check your CA publishes no CRL first
        return chain.Build(cert);
    };
})));
```

- The validation callback decides from `chain.Build`. It must never return `true` on its own.
- **Allowlist and access line,** in one middleware registered first: the certificate is `context.Connection.ClientCertificate` (null when none was sent), the CN `cert.GetNameInfo(X509NameType.SimpleName, false)`; check it against the allowlist file (re-read when it changes; an unreadable file allows nobody); write the access line from [producer.md](producer.md), `probe=<id>` from the `X-TLS-Migration-Probe` header only when it matches `[A-Za-z0-9]{1,8}`, else `-`; answer 403 for an unlisted CN when enforcing.
- **Plain HTTP (stages 2-5):** `k.ListenAnyIP(8080)` added only when `TLS_LEGACY_HTTP_ENABLED` is `true`; at stage 6 written out as `false`. Remove `UseHttpsRedirection` for service callers: a redirect is not support.
- **Health:** `MapHealthChecks` on a separate plain management port (`RequireHost("*:8081")`), bound to the node network.
- **Renewal:** `ServerCertificateSelector` can return a renewed certificate without a restart; otherwise restart after each renewal and say so in the report.
- Tests (`WebApplicationFactory` runs no TLS: test the handshake against Kestrel on a loopback port): listed consumer served; unlisted gets 403; log-only mode serves; a removed line cuts the consumer off; a missing allowlist file allows nobody.

## Consumer

```csharp
var clientCert = X509Certificate2.CreateFromPemFile($"{dir}/client.crt", $"{keyDir}/client.key");
var producerCa = new X509Certificate2($"{dir}/ca-bundle.pem");     // certificate only: the constructor reads PEM
services.AddHttpClient("inventory", c => c.BaseAddress = new Uri(baseUrl))  // baseUrl checked to start with https:// first
    .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler { SslOptions = {
        ClientCertificates = new X509CertificateCollection { clientCert },
        EnabledSslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13,
        CertificateChainPolicy = new X509ChainPolicy {
            TrustMode = X509ChainTrustMode.CustomRootTrust, CustomTrustStore = { producerCa },
            RevocationMode = X509RevocationMode.NoCheck } } });
```

- Throw at start-up when the base address is missing or not `https://`.
- Host name checking stays on: set no `RemoteCertificateValidationCallback`.
- On Windows a key loaded from PEM may need re-importing before TLS can use it: `new X509Certificate2(clientCert.Export(X509ContentType.Pfx))`. Check the version you use.
- A client reads its certificate once: restart after a renewal.
- Tests: the client is built from these files; a blank or `http://` address is refused; a server certificate for another name is refused.

## Files and local

- Paths come from configuration (`TLS_DIR`, `TLS_KEY_DIR`). Keys never live in the repository, in `appsettings*.json` or in user secrets that get committed.
- Local: certificates from `tls-migration/local/certs/` (`<producer>-server.crt`, `<producer>-consumers-ca.crt`, `server-ca.crt` as the consumer's `ca-bundle.pem`, `<producer>-<consumer>.crt`); keys `$TLS_PRIVATE_DIR/local/<producer>/server.key` and `$TLS_PRIVATE_DIR/local/<producer>/<consumer>/client.key`. Put these paths only in local-only files (`.env.local`, `docker-compose.local.yml`): E10 fails `local-dev-` references anywhere else, `appsettings.Development.json` included.
- A call that must stay on plain HTTP gets exactly `// TODO: HTTPS not supported - requires infrastructure update` beside it ([analyse-and-plan.md](analyse-and-plan.md)).

## Never do this

None of these may appear, not even in tests. The gate's scanner looks for most of them; a person or the judge checks the rest:

- `HttpClientHandler.DangerousAcceptAnyServerCertificateValidator`;
- a `ServerCertificateCustomValidationCallback`, `RemoteCertificateValidationCallback` or `ServicePointManager.ServerCertificateValidationCallback` that returns `true` (as a lambda, a block or a method);
- `SslProtocols.Tls`, `SslProtocols.Tls11`, `SslProtocols.Ssl3`;
- on a producer: `AllowAnyClientCertificate()`, and from stage 5 `ClientCertificateMode.NoCertificate` or `AllowCertificate`;
- `curl -k` / `--insecure` in scripts.

## Tests and JUnit XML

E1 reads JUnit-style XML only. `dotnet test` writes TRX by itself, which E1 does not read. The JUnit logger is the `JunitXml.TestLogger` package: if the test project does not already reference it, it is an extra package a person must approve and add; you never install it. Then:

```bash
dotnet test --logger "junit;LogFilePath=build/test-results/{assembly}.xml"
```

Write to `<service>/build/test-results/` and list that folder under `evidence.tests` in the manifest. Check the logger's documentation for the version you use.
