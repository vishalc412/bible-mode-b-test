---
id: reference/glossary
kind: reference
source: [components/catalog/catalog.py, components/catalog/service.py, components/orders/orders.py, components/orders/catalog_client.py, .github/bible/bible_queue.py, tools/plan.py, tools/gate.py, tools/fanout.sh]
summary: Defines the sample-shop and analysis-workflow terms used across the system pages
depends_on: [hld/01-system-context, hld/04-data-architecture, hld/05-key-flows, lld/data-dictionary]
---
# Glossary

| Term | Meaning in this system | Where it appears |
| --- | --- | --- |
| Analysis plan | Versioned JSON inventory of components, source files, tests, functions, HTTP sites, and test baselines. | [`plan.json`](../hld/04-data-architecture.md), [`plan.py`](../lld/tools/plan.md); `tools/plan.py:21-58` |
| Analysis tracker | GitHub issue holding settings and progress for one analysis run. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:316-321,851-855` |
| Agent session issue | Issue assigned to Copilot for a planning, component, assembly, or verification session. | [`bible-mode-b`](../lld/bible-mode-b/README.md); `.github/bible/bible_queue.py:144-151,538-546,771-773` |
| Component branch | Branch named `bible/<component>` used for analysis work before a review PR targets the default branch. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:553-558,608-612` |
| Session PR | Copilot's pull request for one assigned work session; the queue validates it and may merge it into the component branch. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:404-409,659-715` |
| Component review PR | PR from a completed component branch to the default branch for a person to review and merge. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:608-624` |
| Verification report | Markdown artifact carrying a verdict and, for component checks, a fingerprint of the pages reviewed. | [`data dictionary`](../lld/data-dictionary.md); `.github/bible/bible_queue.py:365-378,619-623,749-753` |
| Pages fingerprint | Short hash used to confirm that a verification report concerns the pages currently being checked. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:609-623,707-709` |
| Delta issue | Issue asking for an analysis component to be refreshed after code changes since the baseline. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:790-817` |
| SKU | Identifier used as the key for a product in the in-memory catalog. | [`catalog`](../lld/catalog/catalog.md); `components/catalog/catalog.py:8-12,15-17` |
| Product feed | Supplier JSON response read by `fetch_supplier_feed`; `apply_feed` updates prices and stock for known SKUs. | [`catalog`](../lld/catalog/catalog.md); `components/catalog/catalog.py:36-47` |
| In-process catalog access | Current order helper path, importing the catalog module and calling price and stock functions directly. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:5,19-20,35-42` |
| Remote catalog client | Optional HTTP path for separately deployed orders; its repository callers are tests. | [`catalog client`](../lld/orders/catalog_client.md); `components/orders/catalog_client.py:1-4,19-23`; `components/orders/test_catalog_client.py:37-62` |
| `CATALOG_URL` | Environment setting for the catalog HTTP base URL, defaulting to loopback port 8001. | [`catalog client`](../lld/orders/catalog_client.md), [`configuration`](configuration.md); `components/orders/catalog_client.py:11,14-16` |
| Loyalty discount | Five-percent order discount, used only when it is larger than the bulk discount. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:14,23-32` |
| Bulk discount | Ten-percent discount when total quantity reaches `BULK_THRESHOLD`; it does not stack with the loyalty discount. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:15-16,23-32` |
| Component plan | The `tools` output used to drive component gate and issue fanout. | [`tools`](../lld/tools/README.md); `tools/plan.py:41-58`, `tools/fanout.sh:7-12` |
| Component gate | `tools/gate.py` checks component artifacts and runs unittest discovery for pass 3. | [`gate`](../lld/tools/gate.md); `tools/gate.py:42-78,81-117` |
| Issue fanout | Bash command that creates labels and one component-analysis issue per component in the plan. | [`fanout`](../lld/tools/fanout.md); `tools/fanout.sh:7-30` |
| Image CDN URL | A URL built by `image_url`; catalog code returns it but does not fetch the image. | [`catalog`](../lld/catalog/catalog.md), [`system context`](../hld/01-system-context.md); `components/catalog/catalog.py:6,32-33` |

<!-- cites .github/bible/bible_queue.py@68e91ae09c53c283e7402334cfe2a715785b33ed -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
