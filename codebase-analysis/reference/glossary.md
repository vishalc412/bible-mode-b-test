---
id: reference/glossary
kind: reference
source: [components/catalog/catalog.py, components/catalog/service.py, components/orders/orders.py, components/orders/catalog_client.py, .github/bible/bible_queue.py, tools/plan.py, tools/gate.py, tools/fanout.sh]
summary: Defines the sample-shop and analysis-workflow terms used across the system pages
depends_on: [page:hld/01-system-context.md, page:hld/04-data-architecture.md, page:hld/05-key-flows.md, page:lld/data-dictionary.md]
---
# Glossary

| Term | Meaning in this system | Where it appears |
| --- | --- | --- |
| Analysis plan | Versioned JSON inventory of components, source files, tests, functions, HTTP sites, and test baselines. | [`plan.json`](../hld/04-data-architecture.md), [`plan.py`](../lld/tools/plan.md); `tools/plan.py:21-58` |
| Analysis tracker | GitHub issue holding settings and progress for one analysis run. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:405-425`, `.github/bible/bible_queue.py:1209-1220` |
| Agent session issue | Issue assigned to Copilot for a planning, component, assembly, or verification session. | [`bible-mode-b`](../lld/bible-mode-b/README.md); `.github/bible/bible_queue.py:166-173`, `.github/bible/bible_queue.py:445-449`, `.github/bible/bible_queue.py:535-568` |
| Component branch | Branch named `bible/<component>` used for analysis work before a review PR targets the default branch. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:694-706` |
| Session PR | Copilot's pull request for one assigned work session; the queue validates it and may merge it into the component branch. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:508-514`, `.github/bible/bible_queue.py:821-878` |
| Component review PR | PR from a completed component branch to the default branch for a person to review and merge. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:778-782` |
| Verification report | Markdown artifact carrying a verdict and, for component checks, a fingerprint of the pages reviewed. | [`data dictionary`](../lld/data-dictionary.md); `.github/bible/bible_queue.py:469-482`, `.github/bible/bible_queue.py:777-778`, `.github/bible/bible_queue.py:811-819` |
| Pages fingerprint | Short hash used to confirm that a verification report concerns the pages currently being checked. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:897-900`, `.github/bible/bible_queue.py:778` |
| Delta issue | Issue asking for an analysis component to be refreshed after code changes since the baseline. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:1273-1283` |
| SKU | Identifier used as the key for a product in the in-memory catalog. | [`catalog`](../lld/catalog/catalog.md); `components/catalog/catalog.py:8-12`, `components/catalog/catalog.py:15-17` |
| Product feed | Supplier JSON response read by `fetch_supplier_feed`; `apply_feed` updates prices and stock for known SKUs. | [`catalog`](../lld/catalog/catalog.md); `components/catalog/catalog.py:36-47` |
| In-process catalog access | Current order helper path, importing the catalog module and calling price and stock functions directly. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:5`, `components/orders/orders.py:19-20`, `components/orders/orders.py:35-42` |
| Remote catalog client | Optional HTTP path for separately deployed orders; its repository callers are tests (inferred: its docstring, `components/orders/catalog_client.py:1-4`, names the separate-service use, and a search of the repository finds `catalog_client` used only in `components/orders/test_catalog_client.py`, 6 hits). | [`catalog client`](../lld/orders/catalog_client.md); `components/orders/catalog_client.py:1-4`, `components/orders/catalog_client.py:19-23`; `components/orders/test_catalog_client.py:37-62` |
| `CATALOG_URL` | Environment setting for the catalog HTTP base URL, defaulting to loopback port 8001. | [`catalog client`](../lld/orders/catalog_client.md), [`configuration`](configuration.md); `components/orders/catalog_client.py:11`, `components/orders/catalog_client.py:14-16` |
| Loyalty discount | Five-percent order discount, used only when it is larger than the bulk discount. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:14`, `components/orders/orders.py:23-32` |
| Bulk discount | Ten-percent discount when total quantity reaches `BULK_THRESHOLD`; it does not stack with the loyalty discount. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:15-16`, `components/orders/orders.py:23-32` |
| Component plan | The `tools` output used to drive component gate and issue fanout. | [`tools`](../lld/tools/README.md); `tools/plan.py:41-58`, `tools/fanout.sh:7-12` |
| Component gate | `tools/gate.py` checks component artifacts and runs unittest discovery for pass 3. | [`gate`](../lld/tools/gate.md); `tools/gate.py:42-78`, `tools/gate.py:81-117` |
| Issue fanout | Bash command that creates labels and one component-analysis issue per component in the plan. | [`fanout`](../lld/tools/fanout.md); `tools/fanout.sh:7-30` |
| Image CDN URL | A URL built by `image_url`; catalog code returns it but does not fetch the image (inferred: a search of the repository outside the analysis folder and the skills for `image_url` and `IMAGE_CDN` finds 3 hits, all in `components/catalog/catalog.py`). | [`catalog`](../lld/catalog/catalog.md), [`system context`](../hld/01-system-context.md); `components/catalog/catalog.py:6`, `components/catalog/catalog.py:32-33` |

<!-- cites .github/bible/bible_queue.py@5886e8a4b1928e02dee435ffad7e6f9a1e5ec075 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
