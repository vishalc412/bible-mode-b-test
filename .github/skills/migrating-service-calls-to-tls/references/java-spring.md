# Java and Spring Boot

Contents: producer · consumer · local profile · remove on sight

For servlet applications on embedded Tomcat, Spring Boot 3.2 and later. Record the version and the web stack from the build file first.

| Version | What differs |
| --- | --- |
| 4.x | `RestClient` and `RestTemplate` support moved to the `spring-boot-starter-restclient` starter: add it. `setSslBundle(...)` was removed: use `sslBundle(...)`. Check everything else on this page against the Spring Boot 4.0 migration guide before you rely on it |
| 3.2 and later 3.x | everything below as written |
| 3.1 | SSL bundles exist, but not `RestClient`/`RestClientSsl` (use `RestTemplateBuilder.setSslBundle(...)` or `WebClientSsl`) and not `reload-on-update` (a server certificate renewal needs a restart) |
| 2.7 | no bundles. Server: `server.ssl.certificate`, `server.ssl.certificate-private-key` and `server.ssl.trust-certificate` read the same PEM files. Client: build the `SSLContext` by hand from the PEM files. Every renewal needs a restart |
| before 2.7 | needs a key store, which no script here makes and you must not build from a key yourself: stop and ask |
| WebFlux / Netty, Jetty, Undertow | the connector and the filter below are Tomcat and servlet code. The stages are the same; write the listener and the filter for the stack by hand and say so in the report |

- **A worked, tested example:** the toolkit's `testbench/tls-pair-reference/` (Spring Boot 3.4, run locally).

## Producer

```yaml
server:
  port: 8443
  ssl:
    bundle: server
    client-auth: need            # stages 2-4: want; stage 5 onward: need
spring:
  ssl:
    bundle:
      pem:
        server:
          reload-on-update: true
          options:
            enabled-protocols: TLSv1.2,TLSv1.3   # the protocols Spring uses with a bundle
          keystore:
            certificate: file:${TLS_DIR:/etc/tls}/tls.crt
            private-key: file:${TLS_KEY_DIR:/etc/tls}/tls.key
          truststore:
            certificate: file:${TLS_DIR:/etc/tls}/consumers-ca.crt   # this producer's consumer CA only (<producer>-consumers-ca.crt, mounted under this name: kubernetes.md)
management:
  server:
    port: 8081
    ssl:
      enabled: false             # set explicitly: the management server otherwise inherits server.ssl
  endpoints:
    web:
      exposure:
        include: health
tls:
  migration:
    legacy-http:
      enabled: false             # stages 2-5: true; stage 6: false
      port: 8080
    allowlist:
      file: ${TLS_ALLOWLIST:/etc/tls-migration/allowed-consumers.yaml}
      enforce: true              # stages 2-3: false (log only); stage 4 onward: true
```

`check.sh` (E12) reads these keys: `server.ssl.client-auth`, `server.ssl.bundle`, the bundle's `options.enabled-protocols` and `options.ciphers`, `tls.migration.legacy-http.enabled`, `tls.migration.allowlist.enforce`. Keep the names.

It reads them the way Spring does, from every source, in Spring's order of precedence:

- every `application*.yml` and `.properties` of the module: inside the jar, then outside it (`./`, `./config/`, `./config/*/`), plain files before profile files in each;
- `spring.config.import`: an imported file counts above the file that imports it, and imports inside imports are followed. `spring.config.location` and `spring.config.additional-location` written inside a config file do nothing in Spring (it takes them from the environment, system properties and the command line only): the gate ignores them there and says so in E12's evidence;
- other config-format files under `src/main/resources` (`custom.yml`, `logback-extra.properties`) only when something loads them. Spring never reads such a file by itself. The gate reads it, as an override, when any other file names it: an import, a `@PropertySource`, a Dockerfile `COPY`, a kustomize `configMapGenerator`, a start script. A `bootstrap*.yml` or `.properties` is always read, since Spring Cloud loads it by name. Spring ranks a `@PropertySource` file below the config files; the gate is stricter and judges it as if it won. When the code loads property files in a way the gate cannot follow (an `EnvironmentPostProcessor`, a `PropertySourceLoader`, a `@PropertySource` location with a placeholder or a constant), every such file is read. E12's evidence lists each file as read or not read, with the reason;
- profile files and profile documents, including `!`, `&` and `|` expressions, in the order Spring 3.4 activates them (checked on the reference pair): `spring.profiles.active` is one setting, so the highest-ranking source gives the whole list. The manifest's `producer.profiles` (what the deployment gives as `SPRING_PROFILES_ACTIVE` or `--spring.profiles.active`) and a deployment's own `SPRING_PROFILES_ACTIVE` replace the list in the config files; between files, `application.properties` replaces `application.yml`. The profiles of `spring.profiles.include` come before the active ones, and a group's members come right after the group. The profile listed last wins. A profile that only a replaced list names, or that no list names, is still judged as one a deployment may activate if its file sets a stage key. When includes are set in more than one place, every order of the included profiles is judged. When the order cannot be told at all (an activation inside a profile file or an import), the gate judges the value each profile sets;
- `SPRING_APPLICATION_JSON`, and `spring.config.import` or `spring.config.additional-location` given to the service;
- `spring.config.name` and `spring.config.location`, in any form (environment, `-D`, `--`, `SPRING_APPLICATION_JSON`). These replace the files Spring reads. The gate does not work out the new set, so a run that sets them is "not proven";
- environment variables in deploy files, `ENV` lines in a `Dockerfile`, and `-D` / `--` arguments in start scripts;
- relaxed binding. In a file, `client-auth`, `clientAuth` and `client_auth` are the same setting. The environment-variable spelling `SERVER_SSL_CLIENTAUTH` is the same setting only in the environment: written inside `application.properties` it does nothing, and the gate does not count it. Spring itself binds both `SERVER_SSL_CLIENTAUTH` and `SERVER_SSL_CLIENT_AUTH` from the environment. An existing `SERVER_SSL_CLIENT_AUTH=none` in a deployment is not harmless: it overrides `client-auth`. Find and remove it like the other spelling;
- placeholders. `${inventory.client-auth:need}` is also filled from `INVENTORY_CLIENT_AUTH`, `INVENTORY_CLIENTAUTH` and from a config file that sets `inventory.client-auth`. The gate judges every value it finds.

A setting it can see but not read (a Secret reference, a template) is not guessed. Probes are bound to all of these sources, and to the producer's code and build files: change one and you probe again.

When `server.ssl.bundle` is set, Spring ignores `server.ssl.enabled-protocols` and `server.ssl.ciphers`. The protocols in force are the bundle's `spring.ssl.bundle.pem.<name>.options.enabled-protocols` (and `options.ciphers`). Set them there. E12 reads the bundle's, not `server.ssl.enabled-protocols`.

Keep the `Dockerfile`'s `EXPOSE` in line with what the service listens on: the HTTPS port and the management port, and the plain port only while `legacy-http` is enabled. `EXPOSE` opens nothing, but a stale one misleads whoever deploys the image. Change it before you probe, since the `Dockerfile` is one of the bound sources.

**Health probes.** Put them on the management port in stage 2; this needs `spring-boot-starter-actuator`. The port is reachable from the node network only. `exposure.include` above lists `health` alone: if the service already exposed other endpoints (metrics, `info`, `prometheus`), keep them in the list and tell their users the port changed. Never drop one silently.

**The plain-HTTP connector (stages 2-5).** A conditional customizer adds the second connector:

```java
@Configuration
@ConditionalOnProperty(name = "tls.migration.legacy-http.enabled", havingValue = "true")
public class LegacyHttpConnectorConfig {
    @Bean
    WebServerFactoryCustomizer<TomcatServletWebServerFactory> legacyHttpConnector(
            @Value("${tls.migration.legacy-http.port:8080}") int port) {
        return factory -> {
            Connector connector = new Connector(TomcatServletWebServerFactory.DEFAULT_PROTOCOL);
            connector.setPort(port);
            factory.addAdditionalTomcatConnectors(connector);
        };
    }
}
```

**Allowlist and access line.** One `OncePerRequestFilter` does both. It:

- reads `jakarta.servlet.request.X509Certificate`;
- takes the CN of the first certificate and checks it against `allowed-consumers.yaml`, which it re-reads when the file changes;
- writes the access line ([producer.md](producer.md)), including `probe=<id>` from the `X-TLS-Migration-Probe` header. The probes and the kit's `verify.sh` send a fresh random 8-character id on every run, so the filter must accept any value matching `[A-Za-z0-9]{1,8}` and write `-` for anything else;
- returns 403 for an unlisted CN when `enforce` is true.

An unreadable allowlist file allows nobody: fail closed. Where the service already uses Spring Security, `x509()` with the same lookup may do the 403, but the access line must still be written for every request, with the same fields, and `enforce: false` must still only log: readiness and E8 are built from that line. Keeping the filter is the simpler way.

**Tests to add:**

- listed consumer served;
- unlisted gets 403;
- log-only mode serves;
- removing a line cuts the consumer off;
- a missing file allows nobody.

A `@WebMvcTest` slice picks up the filter. Exclude it there, and test the filter on its own.

## Consumer

```yaml
spring:
  ssl:
    bundle:
      pem:
        inventory-client:                      # named after the producer it calls
          keystore:
            certificate: file:${TLS_DIR:/etc/tls/inventory}/client.crt
            private-key: file:${TLS_KEY_DIR:/etc/tls/inventory}/client.key
          truststore:
            certificate: file:${TLS_DIR:/etc/tls/inventory}/ca-bundle.pem   # the producer's CA only
inventory:
  base-url: ${INVENTORY_BASE_URL}                # no default: a missing address fails at start-up
```

```java
public InventoryClient(RestClient.Builder builder, RestClientSsl ssl,
                       @Value("${inventory.base-url:}") String baseUrl) {
    if (baseUrl.isBlank()) throw new IllegalStateException("inventory.base-url is not set");
    if (!baseUrl.startsWith("https://")) throw new IllegalStateException("inventory.base-url must be https");
    this.restClient = builder.baseUrl(baseUrl).apply(ssl.fromBundle("inventory-client")).build();
}
```

- Use the auto-configured `RestClient.Builder` and `RestClientSsl` (3.2+). For `WebClient`, use `WebClientSsl.fromBundle(...)`. For `RestTemplate`, `RestTemplateBuilder.sslBundle(sslBundles.getBundle("inventory-client"))`; before 3.4 the method is `setSslBundle(...)`.
- Feign, Apache HttpClient and the JDK `HttpClient` have no bundle property: build them from `sslBundles.getBundle("inventory-client").createSslContext()`, in one place, and test that the client uses it.
- **No hot reload for clients.** `reload-on-update` refreshes the embedded web server only. A client built as above reads the bundle once, so a renewed client certificate is presented only after a restart. Either restart the consumer after each renewal (write that into the renewal steps), or set `reload-on-update: true` on the client bundle (`spring.ssl.bundle.pem.inventory-client.reload-on-update: true`) and rebuild the client from `SslBundles.addBundleUpdateHandler("inventory-client", ...)`. The handler is called only for a bundle with `reload-on-update: true`.
- Kubernetes names a TLS Secret's files `tls.crt` and `tls.key`: map them to the names above, or read those names ([kubernetes.md](kubernetes.md), "A consumer's Secret").
- Hostname verification is on by default. Leave it on.
- Remove hard-coded fallback addresses. A missing or plain address fails at start-up.
- Tests: the client is built from the bundle; a blank or plain address is refused; a server certificate for another name is refused.

## Local profile

`application-local.yml` points the bundles at the `local-tls-up.sh` output: certificates in `tls-migration/local/certs/` (`<producer>-server.crt`, `<producer>-<consumer>.crt`), keys in `${TLS_PRIVATE_DIR}/local/<producer>/server.key` and `${TLS_PRIVATE_DIR}/local/<producer>/<consumer>/client.key`, outside the repository. Start the services with `TLS_PRIVATE_DIR` set from `tls-migration/local/private-dir.txt`. This is the only kind of file where local certificate paths may appear.

## Remove on sight

- `TrustAllStrategy`, `TrustSelfSignedStrategy`, `NoopHostnameVerifier`, `InsecureTrustManagerFactory`;
- `X509TrustManager` implementations with empty methods;
- `setHostnameVerifier((h, s) -> true)`;
- `-Dcom.sun.net.ssl.checkRevocation=false`;
- `server.ssl.enabled=false`;
- `client-auth: none`.
