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
| Analysis tracker | GitHub issue holding settings and progress for one analysis run. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:407-427`, `.github/bible/bible_queue.py:1307-1318` |
| Agent session issue | Issue assigned to Copilot for a planning, component, assembly, or verification session. | [`bible-mode-b`](../lld/bible-mode-b/README.md); `.github/bible/bible_queue.py:167-174`, `.github/bible/bible_queue.py:447-451`, `.github/bible/bible_queue.py:595-628` |
| Component branch | Branch named `bible/<component>` used for analysis work before a review PR targets the default branch. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:782-794` |
| Session PR | Copilot's pull request for one assigned work session; the queue validates it and may merge it into the component branch. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:568-574`, `.github/bible/bible_queue.py:911-968` |
| Component review PR | PR from a completed component branch to the default branch for a person to review and merge; created when the component's verification report is accepted and its fingerprint equals the pages' fingerprint. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:867-871` |
| Verification report | Markdown artifact carrying a verdict and, for component checks, a fingerprint of the pages reviewed; the queue also reads its major-correction count, re-check count and accuracy. | [`data dictionary`](../lld/data-dictionary.md); `.github/bible/bible_queue.py:478-507`, `.github/bible/bible_queue.py:865-867`, `.github/bible/bible_queue.py:899-909` |
| Pages fingerprint | Short hash used to confirm that a verification report concerns the pages currently being checked. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:987-990`, `.github/bible/bible_queue.py:867` |
| Accepted report | A verification report that the queue counts as verified: a `PASS`, or a `PASS AFTER CORRECTIONS` with a confirmed re-check. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md#acceptedfacts); `.github/bible/bible_queue.py:523-542` |
| Replayed tracker | A closed analysis tracker labelled `bible-replayed`: the code changes recorded while its run was open are in update issues, or were recorded on the run open at that time. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md#queuereplay_closed_runs); `.github/bible/bible_queue.py:681-697` |
| Delta issue | Issue asking for an analysis component to be refreshed after code changes since the baseline. | [`bible_queue`](../lld/bible-mode-b/bible_queue.md); `.github/bible/bible_queue.py:1371-1381` |
| SKU | Identifier used as the key for a product in the in-memory catalog. | [`catalog`](../lld/catalog/catalog.md); `components/catalog/catalog.py:11-15`, `components/catalog/catalog.py:27-29` |
| Product feed | Supplier JSON response read by `fetch_supplier_feed`; `apply_feed` updates prices and stock for known SKUs. | [`catalog`](../lld/catalog/catalog.md); `components/catalog/catalog.py:48-63` |
| In-process catalog access | Current order helper path, importing the catalog module and calling price and stock functions directly. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:5`, `components/orders/orders.py:19-20`, `components/orders/orders.py:35-42` |
| Remote catalog client | Optional HTTP path for separately deployed orders; its repository callers are tests (inferred: its docstring, `components/orders/catalog_client.py:1-4`, names the separate-service use, and a search of the repository finds `catalog_client` used only in `components/orders/test_catalog_client.py`, 6 hits). | [`catalog client`](../lld/orders/catalog_client.md); `components/orders/catalog_client.py:1-4`, `components/orders/catalog_client.py:19-23`; `components/orders/test_catalog_client.py:37-62` |
| `CATALOG_URL` | Environment setting for the catalog HTTP base URL, defaulting to loopback port 8001. | [`catalog client`](../lld/orders/catalog_client.md), [`configuration`](configuration.md); `components/orders/catalog_client.py:11`, `components/orders/catalog_client.py:14-16` |
| Loyalty discount | Five-percent order discount, used only when it is larger than the bulk discount. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:14`, `components/orders/orders.py:23-32` |
| Bulk discount | Ten-percent discount when total quantity reaches `BULK_THRESHOLD`; it does not stack with the loyalty discount. | [`orders`](../lld/orders/orders.md); `components/orders/orders.py:15-16`, `components/orders/orders.py:23-32` |
| Component plan | The `tools` output used to drive component gate and issue fanout. | [`tools`](../lld/tools/README.md); `tools/plan.py:41-58`, `tools/fanout.sh:7-12` |
| Component gate | `tools/gate.py` checks component artifacts and runs unittest discovery for pass 3. | [`gate`](../lld/tools/gate.md); `tools/gate.py:42-78`, `tools/gate.py:81-117` |
| Issue fanout | Bash command that creates labels and one component-analysis issue per component in the plan. | [`fanout`](../lld/tools/fanout.md); `tools/fanout.sh:7-30` |
| Image CDN URL | A URL built by `image_url`; catalog code returns it but does not fetch the image (inferred: a search of the repository outside the analysis folder and the skills for `image_url` and `IMAGE_CDN` finds 3 hits, all in `components/catalog/catalog.py`). | [`catalog`](../lld/catalog/catalog.md), [`system context`](../hld/01-system-context.md); `components/catalog/catalog.py:9`, `components/catalog/catalog.py:44-45` |

<!-- cites .github/bible/bible_queue.py@a625b4c3353b1744b965b8bbee13e6b3ed5f72a6 -->

<!-- cites components/catalog/catalog.py@75bb1dc767dc16cad9a5ed5555a7293bc004275b -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
