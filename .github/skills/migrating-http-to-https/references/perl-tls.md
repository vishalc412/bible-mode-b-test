# Perl notes for HTTPS migration

## Runtime capability

- Perl reaches TLS through `Net::SSLeay` and `IO::Socket::SSL`, which link to the system OpenSSL.
- TLS 1.2 needs OpenSSL 1.0.1 or later. TLS 1.3 needs OpenSSL 1.1.1 or later.
- Check with: `perl -MNet::SSLeay -e 'print Net::SSLeay::SSLeay_version(), "\n"'`
- Old hosts often carry OpenSSL 0.9.8 or 1.0.0. If so, stop: the fix is a platform change, not a code change.

## Outbound clients

| Library | What HTTPS needs | Verification |
| --- | --- | --- |
| `LWP::UserAgent` | `LWP::Protocol::https` installed (separate distribution), which pulls in `IO::Socket::SSL` and `Mozilla::CA` | On by default in LWP 6+. Remove `ssl_opts => { verify_hostname => 0 }`, `SSL_verify_mode => 0`, and the environment variable `PERL_LWP_SSL_VERIFY_HOSTNAME=0`. |
| `HTTP::Tiny` | `IO::Socket::SSL` 1.56+ and `Net::SSLeay` 1.49+ | Default was **off** before version 0.083. Pass `verify_SSL => 1` explicitly so behaviour does not depend on the installed version. |
| `curl` / `wget` in backticks or `system` | Nothing extra | Remove `-k`, `--insecure`, `--no-check-certificate`. |
| `Net::HTTP`, `IO::Socket::INET` by hand | Rewrite to `IO::Socket::SSL` or a higher-level client | Set `SSL_verify_mode => SSL_VERIFY_PEER`. |

Private certificate authority: pass the CA bundle with `SSL_ca_file` (or `ssl_opts => { SSL_ca_file => ... }`), never by turning verification off.

## Inbound: knowing the request was HTTPS

When TLS terminates at a load balancer or proxy, the application receives plain HTTP and must read the forwarded scheme. Trust it only from the known proxy address.

| Stack | Setting |
| --- | --- |
| Plain CGI | `$ENV{HTTPS}` is not set behind a proxy. Read `$ENV{HTTP_X_FORWARDED_PROTO}`, or have the web server set `HTTPS=on` from that header. |
| PSGI / Plack | `Plack::Middleware::ReverseProxy`, which sets `psgi.url_scheme` from the forwarded headers |
| Mojolicious | `MOJO_REVERSE_PROXY=1` |
| Dancer2 | `behind_proxy: 1` |
| Catalyst | `using_frontend_proxy => 1` |

Search for code that builds absolute URLs from `$ENV{SERVER_PORT}`, `$ENV{SERVER_NAME}` or `CGI->url`; these often produce `http://...:80` behind a proxy.

`CGI.pm`'s `->https` method reads `$ENV{HTTPS}` too, so code using it has the same blind spot. Where changing the code is not wanted, Apache can set the variable from the proxy's header:

```
SetEnvIfExpr "-R '<proxy-address-or-subnet>' && %{HTTP:X-Forwarded-Proto} == 'https'" HTTPS=on
```

The `-R` condition is what makes this safe: the header is believed only when the request comes from the proxy's own address. Do not use the shorter `SetEnvIf X-Forwarded-Proto "^https$" HTTPS=on`. It trusts the header from any host that can reach the application, which is common on flat networks and container platforms. The proxy must also overwrite the header on every request so a client cannot pass its own value through.

## Cookies

- `CGI` / `CGI::Cookie`: `-secure => 1, -httponly => 1, -samesite => 'Lax'`
- Framework session plugins have their own flags; set the equivalent options in config.
- Larger applications usually send every cookie through one wrapper function. Set the flags there, once, instead of at each call site.

## Patterns to search for

```
http://
verify_hostname
SSL_verify_mode
PERL_LWP_SSL_VERIFY_HOSTNAME
verify_SSL
--insecure
--no-check-certificate
SERVER_PORT
```
