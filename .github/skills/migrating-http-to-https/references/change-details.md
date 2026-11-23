# Details for the change steps

Read before Phase 2, step 1.

- **The application's own redirect.** It usually covers only dynamic pages, so static files stay on plain HTTP. Some applications build the redirect URL from the request parameters; for a form POST that copies passwords and API keys into the URL, and from there into access logs and browser history. If the application has its own redirect, the Form POST check in [verification.md](verification.md) shows whether it leaks.
- **`308`** keeps the method and body; `301` turns a POST into a GET for many clients.
- **HSTS in the application** only when the application itself terminates TLS.
- **Health checks.** A plain-HTTP health check receives the redirect once it is on; make the check send the forwarded-scheme header or accept the redirect.
- **Public base URL.** It replaces both hard-coded `http://` own-host URLs and URLs derived from the request environment.
