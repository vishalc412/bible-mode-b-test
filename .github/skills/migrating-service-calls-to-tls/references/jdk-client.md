# Plain JDK: HttpClient, HttpsURLConnection, SSLContext

Contents: consumer · producer · files and local · never do this · tests

The gate's E12 reads Spring Boot configuration only. For this stack E12 reports `not run: stack not read (<stack>)`, so the overall result is at best `not proven` until a person or the judge checks these settings.

For Java code that builds its own `SSLContext` outside Spring's SSL bundles: `java.net.http.HttpClient`, `HttpsURLConnection`, and the JDK's `com.sun.net.httpserver.HttpsServer`. Written for Java 17 and later. Inside a Spring Boot service, prefer a bundle and `createSslContext()` ([java-spring.md](java-spring.md)); this page is for what is left.

## One SSLContext, built from files

The JDK reads PEM certificates with `CertificateFactory`. It has no PEM key reader in Java 17 or 21, so the key file (PKCS#8 PEM, `BEGIN PRIVATE KEY`; the toolkit makes EC P-256 keys) is decoded at start-up. Build it in one place and test that every client uses it.

```java
static SSLContext tlsContext(Path cert, Path key, Path trustedCa) throws Exception {
    CertificateFactory x509 = CertificateFactory.getInstance("X.509");
    Certificate own, ca;
    try (InputStream in = Files.newInputStream(cert)) { own = x509.generateCertificate(in); }
    try (InputStream in = Files.newInputStream(trustedCa)) { ca = x509.generateCertificate(in); }
    String pem = Files.readString(key).replaceAll("-----(BEGIN|END) PRIVATE KEY-----|\\s", "");
    PrivateKey privateKey = KeyFactory.getInstance("EC")
            .generatePrivate(new PKCS8EncodedKeySpec(Base64.getDecoder().decode(pem)));
    char[] inMemory = UUID.randomUUID().toString().toCharArray();   // protects the in-memory store only
    KeyStore keys = KeyStore.getInstance("PKCS12");        // in memory only, never written out
    keys.load(null, null);
    keys.setKeyEntry("self", privateKey, inMemory, new Certificate[] {own});
    KeyManagerFactory kmf = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
    kmf.init(keys, inMemory);
    KeyStore trust = KeyStore.getInstance("PKCS12");       // the one CA, not the JDK's cacerts
    trust.load(null, null);
    trust.setCertificateEntry("ca", ca);
    TrustManagerFactory tmf = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
    tmf.init(trust);
    SSLContext context = SSLContext.getInstance("TLS");
    context.init(kmf.getKeyManagers(), tmf.getTrustManagers(), null);
    return context;
}
```

A file with more than one CA (during a CA rotation) needs `generateCertificates` and one entry per certificate. If the project already uses a PEM reader (Bouncy Castle's `PEMParser`, Netty's `SslContextBuilder`), use that instead. Route B consumers load their PKCS#12 bundle with `KeyStore.getInstance("PKCS12")` and the password from a file whose path comes from configuration.

## Consumer

```java
SSLContext context = tlsContext(Path.of(dir, "client.crt"), Path.of(keyDir, "client.key"), Path.of(dir, "ca-bundle.pem"));
SSLParameters params = new SSLParameters();
params.setProtocols(new String[] {"TLSv1.3", "TLSv1.2"});
HttpClient http = HttpClient.newBuilder().sslContext(context).sslParameters(params)
        .connectTimeout(Duration.ofSeconds(10)).build();
```

- `HttpsURLConnection`: `connection.setSSLSocketFactory(context.getSocketFactory())` on each connection. Never change the JVM-wide defaults (`setDefaultSSLSocketFactory`, `setDefaultHostnameVerifier`).
- Host name checking is on in both by default. Leave it on.
- Read the base URL from configuration; throw at start-up when it is missing or not `https://`.
- A client reads its certificate once: restart after a renewal.
- Tests: the client is built from this context; a blank or `http://` address is refused; a server certificate for another name is refused.

## Producer (`HttpsServer`)

```java
SSLContext context = tlsContext(Path.of(dir, "tls.crt"), Path.of(keyDir, "tls.key"), Path.of(dir, "consumers-ca.crt"));
HttpsServer server = HttpsServer.create(new InetSocketAddress(8443), 0);
server.setHttpsConfigurator(new HttpsConfigurator(context) {
    @Override public void configure(HttpsParameters p) {
        SSLParameters ssl = context.getDefaultSSLParameters();
        ssl.setProtocols(new String[] {"TLSv1.3", "TLSv1.2"});
        if (need) ssl.setNeedClientAuth(true); else ssl.setWantClientAuth(true);   // from TLS_CLIENT_AUTH
        p.setSSLParameters(ssl);
    }
});
```

- Stage settings come from the environment, with the names used on every stack page: `TLS_CLIENT_AUTH` (`want` stages 2-4, `need` from stage 5), `TLS_LEGACY_HTTP_ENABLED` (`true` stages 2-5, `false` stage 6), `TLS_ALLOWLIST` (file path), `TLS_ALLOWLIST_ENFORCE` (`false` stages 2-3, `true` from stage 4).
- **Allowlist and access line,** in a `Filter` on every context: the certificate is `((HttpsExchange) exchange).getSSLSession().getPeerCertificates()[0]` (that call throws when none was sent: catch it and write `cn=-`). Then the same rules as [producer.md](producer.md): allowlist re-read on change, an unreadable file allows nobody, the access line with `probe=<id>` only for `[A-Za-z0-9]{1,8}`, 403 for an unlisted CN when enforcing.
- Plain HTTP (stages 2-5): a second `HttpServer` on the old port, only when `TLS_LEGACY_HTTP_ENABLED` is `true`. Health: a plain server on the management port, bound to the node network.
- Netty, Jetty, Undertow and others: the same stages and context; their switches differ. Check the version you use and say in the report what you wrote by hand.

## Files and local

- Paths come from configuration or the environment (`TLS_DIR`, `TLS_KEY_DIR`). Keys never live in the repository, in resources or in a jar.
- Local: certificates from `tls-migration/local/certs/`; keys `$TLS_PRIVATE_DIR/local/<producer>/server.key` and `$TLS_PRIVATE_DIR/local/<producer>/<consumer>/client.key`, named only in local-only files (`.env.local`, `application-local.*`, `docker-compose.local.yml`). E10 fails `local-dev-` references anywhere else.
- A call that must stay on plain HTTP gets exactly `// TODO: HTTPS not supported - requires infrastructure update` beside it.

## Never do this

None of these may appear, not even in tests. The gate's scanner looks for most of them; a person or the judge checks the rest:

- an `X509TrustManager` with empty checks, `trustAllCerts`, `InsecureTrustManagerFactory`;
- a `HostnameVerifier` that returns `true`, `setEndpointIdentificationAlgorithm(null)` or `("")`;
- `-Djdk.internal.httpclient.disableHostnameVerification`, `-Dcom.sun.net.ssl.checkRevocation=false`;
- `TLSv1` or `TLSv1.1` in `setProtocols`, `jdk.tls.client.protocols` or `https.protocols`;
- on a producer from stage 5: `setNeedClientAuth(false)`.

## Tests and JUnit XML

Maven (Surefire) and Gradle write JUnit XML already, to `target/surefire-reports` and `build/test-results`; E1 reads those. A build without them must have its runner write JUnit XML into a folder listed under `evidence.tests`.
