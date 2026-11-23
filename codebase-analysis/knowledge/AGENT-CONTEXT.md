# bible-mode-b test: agent context

Generated from the analysis snapshot of 2026-11-23, depth deep. The code is the source of truth: open the cited lines before acting on any statement here.

Limits: Calls through dynamic dispatch, callbacks, reflection, string-built names, or another language may not appear in the graph; an absent `CALLS` edge is not proof of no call. `name-unique` and `analysis` edges depend on their resolution and the analysis, so treat them as leads to check. The graph and chunks describe this snapshot; after code changes, refresh the inventory, revise affected pages, and rerun `knowledge.py` (`.github/skills/analyzing-a-codebase/references/knowledge.md`).

## What the system is

The sample catalog/orders application sits beside GitHub Actions tooling that helps repository maintainers create and verify component analyses (`README.md:1-7`; `.github/workflows/bible-plan.yml:7-8`). Repository operators dispatch runs and reviewers inspect pull requests or answer issues; no customer audience for the sample app is declared (`.github/workflows/bible-plan.yml:7-8`; `.github/bible/bible_queue.py:608-627,688-713`). The four components are catalog, orders, `bible-mode-b`, and tools: they provide product lookups/orders, analysis queueing, and planning/gate/fanout functions (`components/catalog/catalog.py:15-47`; `components/orders/orders.py:19-51`; `.github/bible/bible_queue.py:820-867`; `tools/plan.py:21-62`; `tools/gate.py:42-117`; `tools/fanout.sh:1-31`). The catalog has an optional loopback HTTP server; queue jobs run in GitHub Actions on hosted Ubuntu runners, and tools expose local CLI/shell entry points (`components/catalog/service.py:40-49`; `.github/workflows/bible-queue.yml:19-37`; `tools/plan.py:41-62`; `tools/gate.py:81-117`; `tools/fanout.sh:1-31`). Product data is process-local, orders has no durable order store, and queue state lives in GitHub issues, labels, branches, and pull requests (`components/catalog/catalog.py:8-12`; `components/orders/orders.py:45-51`; `.github/bible/bible_queue.py:129-151,396-429,600-624`).

## Components

| Component | Responsibility | Entry points | Key files | Page |
| --- | --- | --- | --- | --- |
| `catalog` | Owns process-local product data, price and stock lookups, supplier-feed helpers, and an optional HTTP API. | `python3 -m components.catalog.service`; `CatalogHandler.do_GET` (`components/catalog/service.py:24-49`) | `components/catalog/catalog.py`, `components/catalog/service.py` | `lld/catalog/README.md` |
| `orders` | Calculates line/order totals, validates stock, sends settlement requests, and has an optional remote catalog client. | Imported functions `line_total`, `order_total`, `validate`, `settle` (`components/orders/orders.py:19-51`) | `components/orders/orders.py`, `components/orders/catalog_client.py` | `lld/orders/README.md` |
| `bible-mode-b` | Starts and reconciles analysis runs, assigns agent issues, validates session results, opens human review PRs, and handles delta updates. | `start`, `reconcile`, `delta` commands (`.github/bible/bible_queue.py:820-867`) | `.github/bible/bible_queue.py`; workflow adapters in `.github/workflows/` | `lld/bible-mode-b/README.md` |
| `tools` | Generates a component plan, checks component artifacts/tests, and fans out component issues. | `python tools/plan.py`, `python tools/gate.py`, `tools/fanout.sh` (`tools/plan.py:41-62`; `tools/gate.py:81-117`; `tools/fanout.sh:1-31`) | `tools/plan.py`, `tools/gate.py`, `tools/fanout.sh` | `lld/tools/README.md` |

## Where to look

| To find | Look in |
| --- | --- |
| Catalog function or HTTP route behavior | `lld/catalog/catalog.md`, `lld/catalog/service.md`, and `lld/api/catalog/catalog.md` |
| Order total, stock, settlement, or remote price behavior | `lld/orders/orders.md` and `lld/orders/catalog_client.md` |
| Queue logic, state, and GitHub API calls | `lld/bible-mode-b/bible_queue.md`; use `hld/05-key-flows.md` for end-to-end sequence |
| Plan, gate, or fanout behavior | `lld/tools/plan.md`, `lld/tools/gate.md`, and `lld/tools/fanout.md` |
| Meaning and ownership of workflow data | `lld/data-dictionary.md` and `hld/04-data-architecture.md` |
| A function's callers and source facts | `knowledge/symbol-index.json`, `knowledge/graph.json`, then the cited function card and code |
| Settings, defaults, and secret names | `reference/configuration.md` |
| System architecture, outbound calls, or failure modes | `hld/01-system-context.md` through `hld/06-cross-cutting.md` |

## Domain vocabulary

- **SKU:** Product identifier and `_PRODUCTS` dictionary key (`components/catalog/catalog.py:8-12,15-17`).
- **Product feed:** Supplier JSON response consumed by `fetch_supplier_feed` and `apply_feed` (`components/catalog/catalog.py:36-47`).
- **In-process catalog access:** Current order path via `components.orders.catalog` (`components/orders/orders.py:5,19-20,35-42`).
- **Remote catalog client:** Optional HTTP price lookup for a separately deployed orders service (`components/orders/catalog_client.py:1-4,19-23`).
- **Loyalty discount:** Five-percent discount selected for a loyal order (`components/orders/orders.py:14,27-29`).
- **Bulk discount:** Ten-percent discount applied at total quantity 10 or more, not stacked with loyalty discount (`components/orders/orders.py:15-16,26-32`).
- **Analysis tracker:** GitHub issue storing the settings and state for one analysis run (`.github/bible/bible_queue.py:316-321,851-855`).
- **Agent session issue:** GitHub issue assigned to Copilot for one analysis or verification session (`.github/bible/bible_queue.py:144-151,538-546,771-773`).
- **Component branch:** Branch named `bible/<component>` holding component analysis work (`.github/bible/bible_queue.py:553-558`).
- **Session PR:** Agent-created pull request whose files and status are checked before the queue merges it into a component branch (`.github/bible/bible_queue.py:404-429,659-715`).
- **Component review PR:** Pull request from a completed component branch to the default branch for a person to review (`.github/bible/bible_queue.py:608-624`).
- **Pages fingerprint:** Value used to ensure a verification report refers to the current component pages (`.github/bible/bible_queue.py:609-623,707-709`).
- **Component plan:** `plan.json`, a versioned inventory of the files, tests, functions, and HTTP sites found for each component (`tools/plan.py:21-58`).
- **Component gate:** `gate.py` validation of analysis artifacts and pass-3 test results (`tools/gate.py:42-78,81-117`).
- **Issue fanout:** `fanout.sh` labels and creates one analysis issue per component in the plan (`tools/fanout.sh:7-30`).
- **Delta issue:** Follow-up issue for a component changed since the saved code-analysis baseline (`.github/bible/bible_queue.py:790-817`).

## Rules the code enforces

### Catalog

1. A price lookup for an unknown SKU raises `KeyError` (`components/catalog/catalog.py:20-24`).
2. Stock is sufficient only when a product exists and its stock is at least the requested quantity (`components/catalog/catalog.py:27-29`).
3. Supplier feed updates affect known SKUs only; absent `products` means no updates (`components/catalog/catalog.py:42-47`).
4. `GET /health` returns the health response with status 200 (`components/catalog/service.py:24-27`).
5. Unknown catalog GET paths return a 404 response (`components/catalog/service.py:33-34`).

### Orders

6. `validate` reports a quantity error for each nonpositive line quantity (`components/orders/orders.py:35-42`).
7. A positive quantity is valid only when catalog stock is sufficient (`components/orders/orders.py:37-42`; `components/catalog/catalog.py:27-29`).
8. Loyal orders use the loyalty discount unless a larger bulk discount applies (`components/orders/orders.py:14-16,23-32`).
9. `remote_line_total` rejects zero or negative quantities with `ValueError` (`components/orders/catalog_client.py:26-29`).
10. `settle` returns true only for an HTTP response with status 200 (`components/orders/orders.py:45-51`).

### Analysis queue

11. A run requires a nonempty verification model different from the analysis model (`.github/bible/bible_queue.py:823-844`).
12. Component selection must be `all` or valid comma-separated component names (`.github/bible/bible_queue.py:845-847`).
13. A new tracker cannot start while another tracker is open (`.github/bible/bible_queue.py:848-850`).
14. A failed agent session gets one retry; a second failure is labelled for human attention and unassigned (`.github/bible/bible_queue.py:464-483`).
15. Chunk and verification PRs may modify only their allowed analysis paths; disallowed files fail the session (`.github/bible/bible_queue.py:659-687`).
16. A component review PR requires a clean `PASS` and a matching nonempty page fingerprint (`.github/bible/bible_queue.py:608-624`).
17. Repeated verification without a clean matching pass leads to a human hold (`.github/bible/bible_queue.py:615-630`).

### Component tools

18. Pass 1 requires `inventory.md` to mention every function in the plan (`tools/gate.py:45-50`).
19. Pass 2 requires every planned HTTP site to be classified `CHANGE` or `KEEP`, with no unresolved `ASK` (`tools/gate.py:51-62`).
20. Pass 3 requires a tests report, an increased count of test functions since plan time, and successful unittest discovery (`tools/gate.py:63-78`).

## Conventions

The sample application and queue are Python modules using the standard library; the analysis toolchain adds Bash and GitHub Actions YAML, with no application package build or production deployment declared (`components/catalog/service.py:7-12`; `.github/bible/bible_queue.py:1-10`; `tools/fanout.sh:1-6`; `hld/02-architecture.md`). Existing tests use `unittest`; the tool gate runs discovery only during component-analysis pass 3, not as a general workflow step (`components/catalog/test_catalog.py:1-12`; `components/orders/test_orders.py:1-12`; `tools/gate.py:63-78`; `.github/workflows/bible-queue.yml:31-37`).

Catalog products are mutable module memory; there is no durable application-side order record. Do not assume process restart persistence or a scheduled feed refresh (`components/catalog/catalog.py:8-12,36-47`; `components/orders/orders.py:45-51`; `hld/04-data-architecture.md`). Orders uses direct catalog calls in the current in-process mode; use `catalog_client.py` only for the documented separate-service path, not as an assumed current caller (`components/orders/orders.py:5,19-20,35-42`; `components/orders/catalog_client.py:1-4,19-23`).

The queue's durable run state is in GitHub issues, labels, branches, and PRs. Workflow jobs check out the default branch, and queue validations inspect component-branch files as data; do not make a PR's code the queue's gate implementation (`.github/workflows/bible-queue.yml:26-30`; `.github/bible/bible_queue.py:723-735`). `tools.plan.py` generates the component plan, `tools.gate.py` reads component artifacts, and `tools.fanout.sh` creates issues; the queue's delta command instead reads `components.json` and a changed-path file (`tools/plan.py:41-58`; `tools/gate.py:42-108`; `tools/fanout.sh:7-30`; `.github/bible/bible_queue.py:790-817,859-861`).

Configuration is mostly environment variables, workflow inputs, and source constants; keep secret values out of files and issue payloads. Workflows map the repository secret `BIBLE_ASSIGN_TOKEN` to `GH_TOKEN`, and the queue sends that value as a bearer token (`.github/workflows/bible-plan.yml:43-53`; `.github/bible/bible_queue.py:89-103`). Use `reference/configuration.md` for all names/defaults; use `hld/03-integrations.md` for protocols, endpoints, authentication, and timeouts.

Errors are not handled uniformly. The catalog HTTP handler maps unknown price SKUs to 404, while direct price lookup raises `KeyError`; the order client and settlement functions generally let network exceptions reach callers (`components/catalog/catalog.py:20-24`; `components/catalog/service.py:28-34`; `components/orders/catalog_client.py:19-23`; `components/orders/orders.py:45-51`). The queue converts GitHub request errors to `RuntimeError`, catches exceptions per tracker, and retries agent sessions once (`.github/bible/bible_queue.py:105-117,485-496,464-483`). Keep these caller-visible behaviors in mind when changing error handling.

Logging is basic: the queue defaults to `print`, the gate prints pass/failure messages, and the catalog HTTP handler suppresses request logs; no metrics or tracing are implemented (`.github/bible/bible_queue.py:397-399`; `tools/gate.py:109-113`; `components/catalog/service.py:36-37`; `hld/06-cross-cutting.md`). Network operations use explicit timeouts but have no general network retry policy (`.github/bible/bible_queue.py:94-117,237-243`; `components/catalog/catalog.py:36-39`; `components/orders/catalog_client.py:19-23`; `components/orders/orders.py:45-50`).

## Hazards

- Settlement, supplier, and remote catalog traffic use plain HTTP; the catalog handlers do not authenticate, and `CATALOG_HOST` can bind beyond loopback. Review deployment and security requirements before exposing these paths (`components/orders/orders.py:7-12,45-50`; `components/catalog/catalog.py:5,36-39`; `components/orders/catalog_client.py:11,19-23`; `components/catalog/service.py:15-43`; `reference/risks-and-surprises.md`).
- Product records live only in memory. Feed entries for unknown SKUs are ignored; missing fields or failed numeric conversions can raise during `apply_feed` (`components/catalog/catalog.py:8-12,42-47`).
- A docstring says the supplier fetch runs nightly from cron, but no scheduler or caller is present in the repository. Do not add assumptions about refresh cadence (`components/catalog/catalog.py:36-39`; `progress.md`, Sweep: Scheduled/background work).
- The order tests do not exercise `order_total`, `validate`, or `settle`; existing test success does not establish those functions' behavior (`components/orders/test_orders.py:6-8`; `components/orders/test_catalog_client.py:37-62`).
- The queue API has no general retry; temporary GitHub failures can stop the current operation. Its agent retry is a distinct workflow rule (`.github/bible/bible_queue.py:94-117,464-483`).
- The queue source extends through line 867, so component-size estimates should be regenerated from the current source rather than assumed current (`.github/bible/bible_queue.py:1-867`; `tools/plan.py:21-58`).
- The catalog handler uses imperative path matching for `GET /health` and `GET /price/<sku>`; do not assume that a static route scan captures these endpoints (`components/catalog/service.py:24-34`).
- The generated fanout instructions reference a `component-analysis` skill path that is not present in the repository; verify it before relying on fanout instructions (`tools/fanout.sh:13-15`).
- The queue `session` docstring omits `start-error`, and the module docstring describes fewer default agent logins than the code configures (`.github/bible/bible_queue.py:36,60,413-429`).
- Mermaid diagrams were checked by reading their syntax, not rendered; diagram and graph readers should validate presentation in their own renderer (`README.md`; `hld/01-system-context.md`).

## Open questions

No unanswered component questions are recorded (`codebase-analysis/reference/open-questions.md:8-14`). The resolved answers establish that both catalog access modes are intentional and the fanout skill path is a stale leftover that must remain unchanged (`components/orders/orders.py:5,19-20,35-42`; `components/orders/catalog_client.py:1-4,19-23`; `tools/fanout.sh:13-15`).

<!-- cites .github/bible/bible_queue.py@3e8cd52b9987123aa99aaaf56def48469224f475 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->

<!-- cites README.md@62b6ccb3c5858e5b699500d9253942283b61da60 -->

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
