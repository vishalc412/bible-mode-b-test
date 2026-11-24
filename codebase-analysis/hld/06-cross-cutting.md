---
id: hld/06-cross-cutting
kind: hld
source:
  - .github/bible/bible_queue.py
  - .github/workflows/bible-plan.yml
  - .github/workflows/bible-queue.yml
  - .github/workflows/bible-delta.yml
  - .github/workflows/poc-assign-copilot.yml
  - components/catalog/catalog.py
  - components/catalog/service.py
  - components/orders/catalog_client.py
  - components/orders/orders.py
  - tools/gate.py
  - tls-migration/01-inventory.md
  - tls-migration/02-certificate-plan.md
  - tls-migration/tls-services.yaml
summary: Credentials, configuration, failures, observability, testing, and deployment practices vary by repository component
depends_on:
  - hld/02-architecture
  - hld/03-integrations
---
# Cross-cutting concerns

## Authentication and authorisation

The GitHub automation authenticates API requests with a bearer token; the catalog and sample order endpoints have no application authentication. The workflow jobs are restricted to the default branch where specified and declare `contents: read`, while the separate assignment token's repository permissions are configured outside this repository.

| Component | How | Evidence |
| --- | --- | --- |
| `bible-mode-b` | Uses `GH_TOKEN` in the GitHub API `Authorization` header. Plan, queue and delta workflows take it from `BIBLE_ASSIGN_TOKEN` and check out the default branch before running the queue code. | `.github/bible/bible_queue.py:105-119`; `.github/workflows/bible-plan.yml:26-45`; `.github/workflows/bible-queue.yml:12-36`; `.github/workflows/bible-delta.yml:14-33` |
| POC assignment | Uses `BIBLE_ASSIGN_TOKEN` as `GH_TOKEN`; the workflow creates the issue through `gh api`. The workflow declares `contents: read` and performs no checkout. | `.github/workflows/poc-assign-copilot.yml:4-8,31-46,66-69` |
| `catalog` | HTTP handlers do not authenticate requests. The server defaults to loopback, but `CATALOG_HOST` can change the bind address. | `components/catalog/service.py:15-34,40-43` |
| `orders` | Settlement and remote catalog requests use plain HTTP; no client credentials or authorization headers are set. | `components/orders/orders.py:7-12,45-50`; `components/orders/catalog_client.py:19-23` |

Consistency: varies (4 variants)

## Secrets

The workflow token is passed to the process through an environment variable, not embedded in workflow source or the issue request payload. The repository code refers to secret names only; the secret value and its provisioning are external.

| Component | How | Evidence |
| --- | --- | --- |
| `bible-mode-b` | Workflows map `secrets.BIBLE_ASSIGN_TOKEN` to `GH_TOKEN`, check it before running, and the API client sends it as a bearer token. | `.github/workflows/bible-plan.yml:43-53`; `.github/workflows/bible-queue.yml:31-37`; `.github/workflows/bible-delta.yml:26-38`; `.github/bible/bible_queue.py:115-119` |
| POC assignment | Shell checks the token; `jq` constructs `request.json` from input values and does not add the token to that JSON. | `.github/workflows/poc-assign-copilot.yml:40-63` |
| Sample application | No application secrets or credential configuration are shown in the catalog or orders modules. | `components/catalog/catalog.py:1-47`; `components/catalog/service.py:1-49`; `components/orders/orders.py:1-51`; `components/orders/catalog_client.py:1-29` |

Consistency: varies (3 variants)

## Configuration

Configuration is split across workflow inputs, environment variables, and source constants; no environment profile or central settings service is declared. The architecture page's configuration table lists the known settings and defaults.

| Component | How | Evidence |
| --- | --- | --- |
| `bible-mode-b` | Workflow inputs select components, models and concurrency; environment variables configure GitHub API access, toolkit location, and optional clock/test settings. | `.github/workflows/bible-plan.yml:9-24,44-49`; `.github/workflows/bible-queue.yml:31-37`; `.github/bible/bible_queue.py:34-36,60-64,91,307-309,397-399` |
| `catalog` | Bind address and port use `CATALOG_HOST` and `CATALOG_PORT`; supplier and image URLs are constants. | `components/catalog/service.py:40-43`; `components/catalog/catalog.py:5-6` |
| `orders` | Catalog base URL uses `CATALOG_URL`; settlement URLs, discounts, bulk threshold and request timeout are function defaults or constants. | `components/orders/catalog_client.py:11,14-23`; `components/orders/orders.py:7-16,45-50` |
| `tools` | Fanout reads `ENGINE` with default `copilot`; plan and gate paths are repository-local. | `tools/fanout.sh:2-12,24-29`; `tools/plan.py:41-58`; `tools/gate.py:81-108` |

Consistency: varies (4 variants)

## TLS migration planning

The repository includes a local catalog–orders TLS migration plan, but it is planning-only: the manifest has `migrator_model: null` and `producer.stage: 0`, and the plan explicitly says that no migration artifacts or gate results have been created (`tls-migration/tls-services.yaml:1-4,18-26`; `tls-migration/02-certificate-plan.md:1-4,45-53`). The inventory identifies the catalog HTTP listener and separate-service orders client as intended migration targets while excluding the supplier and payment calls (`tls-migration/01-inventory.md:8-14,18-33`). This plan does not describe deployed TLS behavior; the current catalog handler and orders HTTP client remain the runtime source of truth (`components/catalog/service.py:24-43`; `components/orders/catalog_client.py:11-23`).

Consistency: planning only; no runtime TLS implementation is evidenced.

## Error handling and resilience

The sample modules generally expose network and data errors to callers; the queue translates GitHub request failures and isolates reconciliation errors per tracker. Session failures get one retry before a human hold, but network requests have no general retry policy.

| Component | How | Evidence |
| --- | --- | --- |
| `catalog` | Unknown products raise `KeyError` in `price_of`; the HTTP handler returns 404 for that error. Supplier-fetch errors and feed parsing errors are not caught here. | `components/catalog/catalog.py:20-24,36-39,42-47`; `components/catalog/service.py:28-34` |
| `orders` | Validation returns per-line errors; unknown SKUs in totals and HTTP/transport errors from settlement or remote price lookup propagate to the caller. | `components/orders/orders.py:23-42,45-51`; `components/orders/catalog_client.py:19-23` |
| `bible-mode-b` | GitHub HTTP and transport errors become `RuntimeError`; reconciliation catches an exception per tracker. Failed agent work is retried once, then labelled for human attention. | `.github/bible/bible_queue.py:105-117,485-496,464-483` |
| `tools` | Gate reports missing or invalid artifacts and failing tests as failures; shell fanout stops on command errors. | `tools/gate.py:42-78,94-117`; `tools/fanout.sh:6,24-30` |

Request timeouts are explicit for GitHub API calls (60 seconds by default, with a 300-second tarball timeout), catalog price lookup (5 seconds), settlement (15 seconds), and supplier feed (10 seconds). There are no retries around these request calls; the queue's one retry is for failed agent sessions, not network requests (`.github/bible/bible_queue.py:94-103,464-483`; `components/orders/catalog_client.py:19-23`; `components/orders/orders.py:45-50`; `components/catalog/catalog.py:36-39`).

Consistency: varies (4 variants)

## Logging, metrics, and tracing

The queue writes progress and error messages to standard output; the catalog HTTP server suppresses its request log messages. No metrics or distributed tracing mechanism is present in the inspected source and workflow configuration.

| Component | How | Evidence |
| --- | --- | --- |
| `bible-mode-b` | Queue defaults its logging callback to `print` and emits tracker and gate status. | `.github/bible/bible_queue.py:396-399,491-496,721-729,780-788` |
| `catalog` | `CatalogHandler.log_message` is a no-op. | `components/catalog/service.py:36-37` |
| Sample application and tools | No logging framework, metrics, or tracing calls were found in the repository sweep. | `codebase-analysis/progress.md` (Sweep: Outbound Python, Entry points, and Security dispositions) |

Consistency: varies (2 variants)

## Build, deployment, and dependencies

The sample application and tools run from source without a declared package build; GitHub Actions uses hosted Ubuntu runners. The repository's application and queue code use Python's standard library, while workflows also invoke GitHub Actions, `gh`, and `jq`.

| Component | How | Evidence |
| --- | --- | --- |
| `catalog` and `orders` | Python source modules; the catalog server is started with `python3 -m components.catalog.service`. No application packaging or deployment manifest is identified in the component pages. | `components/catalog/service.py:1-12,40-49`; `components/orders/orders.py:1-5`; `codebase-analysis/lld/catalog/README.md`; `codebase-analysis/lld/orders/README.md` |
| `bible-mode-b` | Python queue runs on `ubuntu-latest` after checkout; workflow job timeouts and concurrency are defined in YAML. | `.github/workflows/bible-plan.yml:29-40`; `.github/workflows/bible-queue.yml:15-30`; `.github/bible/bible_queue.py:1244-1262` |
| `tools` | Python scripts and Bash run from the repository; fanout invokes `gh`. | `tools/plan.py:41-62`; `tools/gate.py:81-117`; `tools/fanout.sh:1-31` |

Consistency: varies (3 variants)

## Testing

The sample components use Python's `unittest`; the tool gate runs discovery for pass 3. No repository Actions workflow in the inventory invokes that test command automatically.

| Component | How | Evidence |
| --- | --- | --- |
| `catalog` and `orders` | Tests are `unittest.TestCase` modules; orders' catalog-client tests start a local HTTP server. | `components/catalog/test_catalog.py:1-12`; `components/orders/test_orders.py:1-12`; `components/orders/test_catalog_client.py:1-66` |
| `tools` | Pass 3 of the gate invokes `python -m unittest discover`. | `tools/gate.py:63-78` |
| `bible-mode-b` | Workflows run the queue, plan or delta command; none invokes the application test suite. | `.github/workflows/bible-plan.yml:50-54`; `.github/workflows/bible-queue.yml:31-37`; `.github/workflows/bible-delta.yml:26-38` |

Consistency: varies (3 variants)

<!-- cites .github/bible/bible_queue.py@9084f4915d286441c5b3a9a29a8df059bf76dacc -->

<!-- cites .github/workflows/bible-delta.yml@5317a1ada61df3db98cc21d8db6d1415fe732c58 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->

<!-- cites .github/workflows/poc-assign-copilot.yml@dab60e0d846bfee50726dce662df48fc186ca3d3 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/catalog/test_catalog.py@9be40d147e425d178067c8b34f19b28b9b374d1f -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites components/orders/test_orders.py@ca9144cf39abe39e988dc009863b036a7ee1a39f -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
