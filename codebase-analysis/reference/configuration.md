---
id: reference/configuration
kind: reference
source: [components/catalog/catalog.py, components/catalog/service.py, components/orders/orders.py, components/orders/catalog_client.py, .github/bible/bible_queue.py, .github/workflows/bible-plan.yml, .github/workflows/bible-queue.yml, .github/workflows/bible-delta.yml, .github/workflows/poc-assign-copilot.yml, tools/fanout.sh]
summary: Lists configuration inputs, defaults, and their read and set locations without secret values
depends_on: [hld/02-architecture, hld/06-cross-cutting]
---
# Configuration

Secret values are not recorded here. `BIBLE_ASSIGN_TOKEN` is configured as a repository secret; the workflows expose it to their processes as `GH_TOKEN` (`.github/workflows/bible-plan.yml:43-53`; `.github/workflows/bible-queue.yml:31-37`; `.github/workflows/bible-delta.yml:26-38`; `.github/workflows/poc-assign-copilot.yml:40-52`).

| Key or variable | Purpose | Default | Read in | Set in | Secret? |
| --- | --- | --- | --- | --- | --- |
| `CATALOG_HOST` | Catalog HTTP server bind host | `127.0.0.1` | `components/catalog/service.py:40-41` | Environment or `make_server` argument | No |
| `CATALOG_PORT` | Catalog HTTP server bind port | `8001` | `components/catalog/service.py:40-43` | Environment or `make_server` argument | No |
| `SUPPLIER_FEED_URL` | Supplier product JSON endpoint | `http://feeds.supplier-one.example.com/v2/products.json` | `components/catalog/catalog.py:5,36-39` | Source constant | No |
| `IMAGE_CDN` | Prefix used to construct product image URLs; not fetched | `https://cdn.example.com/img/` | `components/catalog/catalog.py:6,32-33` | Source constant | No |
| `CATALOG_URL` | Catalog HTTP API base URL | `http://127.0.0.1:8001` | `components/orders/catalog_client.py:14-23` | Environment; tests set it for the local server | No |
| `PARTNER_SETTLE_URL` | Settlement partner endpoint | `http://partner-legacy.internal/settle` | `components/orders/orders.py:7-9,45-50` | Source constant | No |
| `DEV_SETTLE_URL` | Local development settlement endpoint | `http://localhost:8099/settle` | `components/orders/orders.py:11-12,45-50` | Source constant | No |
| `LOYALTY_DISCOUNT` | Loyalty discount fraction | `0.05` | `components/orders/orders.py:14,27-29` | Source constant | No |
| `BULK_DISCOUNT` | Bulk discount fraction | `0.10` | `components/orders/orders.py:15,30-31` | Source constant | No |
| `BULK_THRESHOLD` | Total quantity that selects the bulk discount | `10` | `components/orders/orders.py:16,26,30` | Source constant | No |
| `timeout` in `fetch_supplier_feed` | Supplier request timeout in seconds | `10` | `components/catalog/catalog.py:36-39` | Function argument | No |
| `timeout` in `remote_price` | Catalog HTTP request timeout in seconds | `5` | `components/orders/catalog_client.py:19-23` | Function argument | No |
| `timeout` in `settle` | Settlement request timeout in seconds | `15` | `components/orders/orders.py:45-50` | Function argument | No |
| `dev` | Selects the local settlement URL when true | `False` | `components/orders/orders.py:45-50` | Function argument | No |
| `GITHUB_API_URL` | GitHub API base URL | `https://api.github.com` | `.github/bible/bible_queue.py:105-119` | Environment; optional constructor argument overrides it | No |
| GitHub API `timeout` | Queue request timeout in seconds | `60`; tarball request uses `300` | `.github/bible/bible_queue.py:94-103,237-243` | Function argument | No |
| `GITHUB_REPOSITORY` | Repository owner and name for queue operations | Required; none | `.github/bible/bible_queue.py:1260-1264` | GitHub Actions environment | No |
| `BIBLE_ASSIGN_TOKEN` | Credential used to assign Copilot and make queue API calls | Required repository secret; value not documented | Workflow job environments | Repository secret settings | Yes |
| `GH_TOKEN` | GitHub API bearer-token environment variable used by `gh` or the queue client | Required; supplied from `BIBLE_ASSIGN_TOKEN` in workflows | `.github/bible/bible_queue.py:1260-1264`; POC workflow shell | Workflow environment | Yes |
| `BIBLE_AGENT_LOGINS` | Agent logins recognized by the queue | `Copilot,copilot-swe-agent[bot],copilot-swe-agent` | `.github/bible/bible_queue.py:61` | Environment | No |
| `BIBLE_AGENT_APP` | GitHub app slug used to identify agent events | `copilot-swe-agent` | `.github/bible/bible_queue.py:62-65` | Environment | No |
| `BIBLE_NOW` | Test clock override | Current UTC time when unset | `.github/bible/bible_queue.py:352-354` | Environment | No |
| `BIBLE_SKILLS` | Path to the analysis toolkit | `.github/skills` | `.github/bible/bible_queue.py:474-476` | Environment | No |
| `components` | Components selected for an analysis run | `all` | `.github/bible/bible_queue.py:1247-1252` | `bible-plan` workflow input | No |
| `model` | Model for analysis sessions | Empty, meaning agent default | `.github/bible/bible_queue.py:1247-1252`; workflow inputs | `.github/workflows/bible-plan.yml:14-17`; `.github/workflows/poc-assign-copilot.yml:26-29` | No |
| `verify_model` | Required model for verification, different from analysis model | Required | `.github/bible/bible_queue.py:1247-1268` | `bible-plan` workflow input | No |
| `concurrency` | Maximum active components; zero means no cap | `0` | `.github/bible/bible_queue.py:823-828,524-529` | `bible-plan` workflow input | No |
| `COMPONENTS` | Component selection forwarded to the queue CLI | Value of `inputs.components` | `.github/workflows/bible-plan.yml:44-49,53-54` | `bible-plan` step environment | No |
| `MODEL` | Analysis model forwarded to the queue CLI or POC assignment payload | Value of the model input | `.github/workflows/bible-plan.yml:44-54`; `.github/workflows/poc-assign-copilot.yml:40-63` | Workflow step environment | No |
| `VERIFY_MODEL` | Separate verification model forwarded to the queue CLI | Value of `inputs.verify_model` | `.github/workflows/bible-plan.yml:44-54` | `bible-plan` step environment | No |
| `CONCURRENCY` | Active-component limit forwarded to the queue CLI | Value of `inputs.concurrency` | `.github/workflows/bible-plan.yml:44-54` | `bible-plan` step environment | No |
| `--analysis` | Analysis output directory | `codebase-analysis` | `.github/bible/bible_queue.py:828,833` | Queue CLI option | No |
| `--depth` | Analysis depth | `deep` | `.github/bible/bible_queue.py:1253` | Queue CLI option | No |
| `--changed-file` | File containing one changed repository path per line | Required | `.github/bible/bible_queue.py:831-833,859-861` | Delta CLI option | No |
| `--pass` | Gate pass number to run | Unset means use `status.json` passes | `tools/gate.py:81-103` | Gate CLI option | No |
| `title` | POC issue title | `POC: Copilot assigned by a workflow` | `.github/workflows/poc-assign-copilot.yml:13-17` | POC workflow input | No |
| `task` | POC issue body/task | Default task text in workflow | `.github/workflows/poc-assign-copilot.yml:18-21` | POC workflow input | No |
| `base_branch` | Branch Copilot starts from for the POC issue | `main` | `.github/workflows/poc-assign-copilot.yml:22-25` | POC workflow input | No |
| `ENGINE` | Fanout issue-assignment engine | `copilot` | `tools/fanout.sh:7-8,24-29` | Environment | No |
| `repo` | GitHub repository targeted by fanout | Required positional `owner/repo` | `tools/fanout.sh:2-8,10-12` | Command-line argument | No |
| `BEFORE`, `AFTER` | Push commit range for delta processing | GitHub event values | `.github/workflows/bible-delta.yml:27-38` | Workflow event environment | No |
| `RUNNER_TEMP` | Temporary file location for changed paths | GitHub-hosted runner value | `.github/workflows/bible-delta.yml:31-38` | GitHub Actions runner | No |
| `TITLE` | POC issue title passed to `jq` | `inputs.title` | `.github/workflows/poc-assign-copilot.yml:40-44,53-63` | POC workflow step environment | No |
| `TASK` | POC issue body passed to `jq` | `inputs.task` | `.github/workflows/poc-assign-copilot.yml:40-44,53-63` | POC workflow step environment | No |
| `BASE` | Target branch supplied in the POC assignment payload | `inputs.base_branch` | `.github/workflows/poc-assign-copilot.yml:40-45,53-63` | POC workflow step environment | No |
| `REPO` | Target repository passed to `gh api` | Current workflow repository | `.github/workflows/poc-assign-copilot.yml:40-43,53-69` | POC workflow step environment | No |
| `permissions.contents` | GitHub Actions token permission declared by the workflows | `read` | Workflow permissions blocks | `.github/workflows/bible-plan.yml:26-27`; `.github/workflows/bible-queue.yml:12-13`; `.github/workflows/bible-delta.yml:14-15`; `.github/workflows/poc-assign-copilot.yml:31-32` | No |
| `runs-on` | GitHub Actions runner image | `ubuntu-latest` | Workflow job declarations | `.github/workflows/bible-plan.yml:34-38`; `.github/workflows/bible-queue.yml:19-24`; `.github/workflows/bible-delta.yml:17-21`; `.github/workflows/poc-assign-copilot.yml:34-37` | No |
| `timeout-minutes` | Maximum job duration | `15` plan/delta, `20` queue, `5` POC | Workflow job declarations | Same workflow job declarations above | No |
| `concurrency.group` | Prevents overlapping plan or queue workflow runs | `bible-plan`, `bible-queue`; cancellation disabled | Workflow concurrency blocks | `.github/workflows/bible-plan.yml:29-32`; `.github/workflows/bible-queue.yml:15-18` | No |

<!-- cites .github/bible/bible_queue.py@9084f4915d286441c5b3a9a29a8df059bf76dacc -->

<!-- cites .github/workflows/bible-delta.yml@5317a1ada61df3db98cc21d8db6d1415fe732c58 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->

<!-- cites .github/workflows/poc-assign-copilot.yml@dab60e0d846bfee50726dce662df48fc186ca3d3 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->
