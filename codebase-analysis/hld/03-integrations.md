---
id: hld/03-integrations
kind: hld
source:
  - components/catalog/service.py
  - components/catalog/catalog.py
  - components/orders/orders.py
  - components/orders/catalog_client.py
  - .github/bible/bible_queue.py
  - .github/workflows/bible-plan.yml
  - .github/workflows/bible-queue.yml
  - .github/workflows/bible-delta.yml
  - .github/workflows/poc-assign-copilot.yml
  - tools/fanout.sh
summary: Catalog routes, workflow triggers, and outbound calls across the sample services and GitHub automation
depends_on:
  - hld/01-system-context
  - hld/02-architecture
---
# Integrations

## Inbound interfaces

| Component | Interface | Kind | Exposed to | Authentication | Card | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `catalog` | `GET /health` | HTTP route | Any network client that can reach the bind address | None in handler | [Catalog endpoint](../lld/api/catalog/catalog.md#get-health) | `components/catalog/service.py:24-27,40-43` |
| `catalog` | `GET /price/<sku>` | HTTP route | Any network client that can reach the bind address | None in handler | [Catalog endpoint](../lld/api/catalog/catalog.md#get-pricesku) | `components/catalog/service.py:28-34,40-43` |
| `bible-mode-b` | `bible-plan` manual dispatch | GitHub Actions event | Repository operators | GitHub workflow access; no workflow-level identity condition beyond default-branch check | [Component design](../lld/bible-mode-b/README.md) | `.github/workflows/bible-plan.yml:7-8,37-54` |
| `bible-mode-b` | `bible-queue` every 15 minutes or manual dispatch | Scheduled or manual workflow event | GitHub Actions | GitHub workflow access; job is restricted to the default branch | [Component design](../lld/bible-mode-b/README.md) | `.github/workflows/bible-queue.yml:7-10,23-37` |
| `bible-mode-b` | `bible-delta` default-branch push | GitHub Actions event | Repository pushes other than ignored paths | Job is restricted to the default branch | [Component design](../lld/bible-mode-b/README.md) | `.github/workflows/bible-delta.yml:6-10,18-36` |
| POC workflow | Manual dispatch with title, task, base branch and model | GitHub Actions event | Repository operators | GitHub workflow access; uses the repository secret for the API call | [Component design](../lld/bible-mode-b/README.md) | `.github/workflows/poc-assign-copilot.yml:11-29,34-69` |
| `orders` | `line_total`, `order_total`, `validate`, `settle` | Python library functions | Importing Python code; no HTTP route is declared | None in these functions | [Orders module](../lld/orders/orders.md) | `components/orders/orders.py:19-51` |
| `tools` | `python tools/plan.py`, `python tools/gate.py ...`, `tools/fanout.sh ...` | CLI commands | Local operator or automation invoking the commands | Shell/runner access; `gh` uses its configured auth | [Tools design](../lld/tools/README.md) | `tools/plan.py:41-62`; `tools/gate.py:81-117`; `tools/fanout.sh:2-5` |
| `bible-mode-b` | `bible_queue.py start`, `reconcile`, `delta` | CLI commands invoked by the start, queue and delta workflows | GitHub Actions runner or a local operator | Requires `GITHUB_REPOSITORY` and `GH_TOKEN` | [Queue module](../lld/bible-mode-b/bible_queue.md#main) | `.github/bible/bible_queue.py:1244-1294`; `.github/workflows/bible-plan.yml:44-54`; `.github/workflows/bible-queue.yml:31-37`; `.github/workflows/bible-delta.yml:25-38` |

The catalog API binds to `127.0.0.1` on port 8001 by default, configurable with `CATALOG_HOST` and `CATALOG_PORT`; no TLS or authentication is configured in the handler (`components/catalog/service.py:1-5,24-43`).

## Outbound calls

| From | To | Purpose | Protocol | Scheme | Port | Address from | Authentication | Timeout, retry | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `catalog.fetch_supplier_feed` | Supplier One feed | Reads product JSON | HTTP | HTTP | 80 implicit | `SUPPLIER_FEED_URL` constant | None shown | Default 10 seconds; no retry or fallback | `components/catalog/catalog.py:5,36-39` |
| `orders` | `catalog` Python module | Reads price and stock in the current in-process mode | Python call | N/A | N/A | `from components.catalog import catalog` | Process-local | No network timeout or retry | `components/orders/orders.py:5,19-20,35-42` |
| `orders.catalog_client` | Catalog HTTP API | Reads one SKU price in separate-service mode | HTTP | HTTP | 8001 by default; URL may override | `CATALOG_URL`, default `http://127.0.0.1:8001` | None shown | Default 5 seconds; no retry or fallback | `components/orders/catalog_client.py:11,14-23`; `components/catalog/service.py:40-43` |
| `orders.settle` | Payment partner | Sends JSON order settlement | HTTP | HTTP | 80 implicit | `PARTNER_SETTLE_URL` constant | None shown | Default 15 seconds; no retry or fallback | `components/orders/orders.py:7-9,45-51` |
| `orders.settle(dev=True)` | Local development fake | Sends the same settlement payload for development | HTTP | HTTP | 8099 | `DEV_SETTLE_URL` constant | None shown | Default 15 seconds; no retry or fallback | `components/orders/orders.py:12,45-51` |
| `bible-mode-b` | GitHub API | Issues, labels, branches, contents, PRs, timelines, commits, tarballs, GraphQL ready-for-review | REST and GraphQL | HTTPS by default | 443 by default | `GITHUB_API_URL`, default `https://api.github.com` | GitHub token from `GH_TOKEN` | Request timeout 60 seconds; tarball 300 seconds; no retry; optional 404 fallback in `GitHub.call` | `.github/bible/bible_queue.py:91-117,129-302` |
| POC workflow | GitHub Issues API | Creates an issue and assigns Copilot | REST through `gh api` | GitHub API HTTPS | 443 by default | `REPO` and GitHub CLI API base | `BIBLE_ASSIGN_TOKEN` in `GH_TOKEN` | No timeout or retry specified in the workflow | `.github/workflows/poc-assign-copilot.yml:40-69` |
| `tools/fanout.sh` | GitHub CLI (`gh`) | Creates engine/component labels and issues | CLI; network transport is not specified in the script | Not specified | Not specified | Supplied `owner/repo` argument | `gh` configuration; not specified in the script | No timeout or retry specified | `tools/fanout.sh:7-29` |
| `bible-mode-b` | Analysis toolkit scripts and helpers under `BIBLE_SKILLS` | Maps changed files; checks component coverage and reads page fingerprint | In-process Python import and local subprocess | Local process | N/A | `BIBLE_SKILLS`, default `.github/skills` | Same runner filesystem | No subprocess timeout is passed | `.github/bible/bible_queue.py:397-399,698-735,794-802` |

`image_url` returns a URL under `IMAGE_CDN` but performs no network request, so it is not counted as an outbound connection (`components/catalog/catalog.py:6,32-33`).

## Dependency matrix

| From | To | Dependency | Evidence |
| --- | --- | --- | --- |
| `orders` | `catalog` | Direct in-process price/stock calls; optional HTTP price client is exercised by tests and intended for separate services | `components/orders/orders.py:5,19-20,35-42`; `components/orders/catalog_client.py:14-23`; `components/orders/test_catalog_client.py:37-62` |
| `catalog` | Supplier One | Supplier JSON fetch when explicitly invoked; no in-repository schedule or caller is shown | `components/catalog/catalog.py:36-47`; `codebase-analysis/lld/catalog/README.md:149,157` |
| `orders` | Payment partner | Settlement POST | `components/orders/orders.py:45-51` |
| `bible-mode-b` | GitHub and Copilot | Stores run state and creates/assigns sessions; agent returns work through issue timelines and PRs | `.github/bible/bible_queue.py:129-151,195-220,538-571,738-774` |
| `bible-mode-b` | Analysis toolkit | Imports component helpers and runs coverage/status scripts | `.github/bible/bible_queue.py:397-399,698-735,794-802` |
| `tools` | GitHub CLI | Creates component labels and issues from `plan.json` | `tools/fanout.sh:7-29` |
| `tools.plan` | `tools.gate` | Uses the same test counter while generating the plan baseline | `tools/plan.py:15,36-38`; `tools/gate.py:33-39` |

<!-- cites .github/bible/bible_queue.py@9084f4915d286441c5b3a9a29a8df059bf76dacc -->

<!-- cites .github/workflows/bible-delta.yml@5317a1ada61df3db98cc21d8db6d1415fe732c58 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->

<!-- cites .github/workflows/poc-assign-copilot.yml@dab60e0d846bfee50726dce662df48fc186ca3d3 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
