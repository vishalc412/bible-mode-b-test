# Where to terminate TLS

Pick one per application and record it at the top of `https-inventory.md`.

| Option | How | Good when | Watch for |
| --- | --- | --- | --- |
| **Cloud load balancer** | AWS Application Load Balancer with an ACM certificate; Azure Application Gateway or Front Door; Google Cloud Application Load Balancer with a managed certificate | The app is moving to cloud anyway; certificates renew automatically | App must read the forwarded scheme; traffic from balancer to app is plain HTTP unless re-encrypted |
| **Reverse proxy on the host** | nginx, Apache httpd or HAProxy in front of the app | On-prem, or as an interim step before a cloud move | Certificate renewal is yours to automate |
| **In the application** | The app server itself holds the certificate | Small services with no proxy; end-to-end encryption required | Legacy runtimes with old TLS libraries; certificate handling in app config |

Default recommendation: terminate at a load balancer or proxy. It keeps certificate handling out of legacy code and works even when the application's own TLS library is old.

If policy requires encryption all the way to the application, use the first or second option and re-encrypt to the app, which then also needs a certificate.
