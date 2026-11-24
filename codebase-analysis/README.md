---
id: README
kind: reference
source: [README.md, components/catalog/catalog.py, components/catalog/service.py, components/orders/orders.py, .github/bible/bible_queue.py, tools/plan.py, tools/gate.py, tools/fanout.sh]
summary: Entry point for the system analysis, its component pages, evidence, and operational references
depends_on: [page:00-mind-map.md, page:hld/01-system-context.md, page:hld/02-architecture.md, page:reference/configuration.md]
---
# bible-mode-b test: system reference

Status: CORRECTED AFTER VERIFICATION (report of 2026-11-24; about 470 statements added or changed since, not re-verified; each is accounted for in `revision-log.md`).

| | |
| --- | --- |
| Depth | Deep for all four components |
| Version given by the user | Not provided |
| Snapshot | 24 in-scope files, 1,812 source lines, the code of 2026-11-24 (the queue file has 1,336 lines) |
| Coverage | `coverage.py` of 2026-11-24, after the corrections: result PASS at deep, 116/116 symbols, 98/98 functions with a full card, 320/320 branch lines, 232/232 call-graph edges, 2,969/2,969 citations (one per range since the multi-range citations were split), 17/17 front-matter pages, 2/2 calls into other components |
| Produced with | Copilot coding agent (model not recorded) for planning, the components, assembly and the first revisions; Claude Sonnet 5.5 standing in for Copilot for the revisions of 24 Nov 2026 afternoon (#96 finish, #101), when the account's Copilot AI credits were used up |
| Diagrams | Checked by reading only; no Mermaid renderer was available |

## In two minutes

The repository combines a sample catalog/orders application with a separate GitHub Actions workflow system for producing and maintaining codebase analyses; the modules share a repository but are not one deployed service (`README.md:1-7`; [`system context`](hld/01-system-context.md)). The catalog keeps product records in process memory, provides price and stock lookups, and includes an optional HTTP server (`components/catalog/catalog.py:8-29`; `components/catalog/service.py:15-49`). The current order helpers import the catalog directly, while the HTTP price client is intended for a separately deployed orders service and is called only by tests in this repository (`components/orders/orders.py:5`, `components/orders/orders.py:19-20`, `components/orders/orders.py:35-42`; `components/orders/catalog_client.py:1-4`, `components/orders/catalog_client.py:19-23`; `components/orders/test_catalog_client.py:37-62`). Orders computes totals, validates stock, and sends settlement requests to a partner or local development endpoint (`components/orders/orders.py:19-51`). The `bible-mode-b` queue uses GitHub issues, branches, and pull requests to assign Copilot work, inspect artifacts, and coordinate human review (`.github/bible/bible_queue.py:127-153`, `.github/bible/bible_queue.py:405-425`, `.github/bible/bible_queue.py:617-668`). The `tools` commands generate a component plan, validate component artifacts, and create component issues (`tools/plan.py:21-58`; `tools/gate.py:42-78`; `tools/fanout.sh:7-30`). GitHub Actions runs the queue and related automation on hosted Ubuntu runners; no production deployment topology for catalog or orders is declared (`.github/workflows/bible-queue.yml:19-37`; [`architecture`](hld/02-architecture.md)). The main operational cautions are plain-HTTP supplier and payment calls, unauthenticated catalog routes, process-local product data, and no source evidence for the supplier feed's claimed nightly schedule (`components/catalog/catalog.py:5`, `components/catalog/catalog.py:36-47`; `components/catalog/service.py:24-43`; `components/orders/orders.py:7-12`, `components/orders/orders.py:45-50`).

## At a glance

The context diagram shows the application's direct calls and the workflow system's GitHub-mediated work; the CDN is a URL target only.

```mermaid
flowchart LR
  operator(["Repository operator<br/>starts runs, reviews PRs, answers questions"])
  reviewer(["Repository reviewer"])
  subgraph repo["bible-mode-b-test repository"]
    catalog["catalog<br/>Python module and optional HTTP service"]
    orders["orders<br/>Python library and HTTP client"]
    queue["bible-mode-b<br/>GitHub Actions workflow and Python queue"]
    tools["tools<br/>planning, gate, and fanout"]
  end
  github{{"GitHub<br/>Actions, issues, repository and PRs"}}
  copilot{{"Copilot coding agent<br/>assigned to workflow issues"}}
  supplier{{"Supplier One<br/>product JSON feed"}}
  partner{{"Payment partner<br/>settlement endpoint"}}
  devsettle{{"Local settle fake<br/>development only"}}
  cdn{{"Image CDN<br/>URL target only, not fetched"}}
  operator -->|"manual workflow dispatch"| github
  reviewer -->|"reviews PRs and answers issues"| github
  github -->|"runs workflows from the repository"| queue
  queue -->|"REST and GraphQL over HTTPS, issue and repository state"| github
  tools -->|"gh CLI, labels and issues, transport not stated"| github
  github -->|"issue assignment"| copilot
  copilot -->|"session PRs and commits"| github
  orders -->|"in-process catalog calls"| catalog
  catalog -->|"product JSON, HTTP"| supplier
  orders -->|"settlement JSON, HTTP"| partner
  orders -->|"settlement JSON, HTTP, only when dev is set"| devsettle
  catalog -.->|"returns constructed image URL, no request"| cdn
```

| Element | Evidence |
| --- | --- |
| Operator and reviewer actions | `.github/workflows/bible-plan.yml:7-8`; `.github/bible/bible_queue.py:648-668`, `.github/bible/bible_queue.py:711-719` |
| GitHub workflow, issue and repository interactions | `.github/workflows/bible-queue.yml:7-37`; `.github/bible/bible_queue.py:92-105`, `.github/bible/bible_queue.py:127-153` |
| Copilot assignment and session PRs | `.github/bible/bible_queue.py:166-173`, `.github/bible/bible_queue.py:445-449`, `.github/bible/bible_queue.py:508-533` |
| Orders to catalog | `components/orders/orders.py:5`, `components/orders/orders.py:19-20`, `components/orders/orders.py:35-42` |
| Catalog to supplier feed | `components/catalog/catalog.py:5`, `components/catalog/catalog.py:36-39` |
| Orders to payment partner | `components/orders/orders.py:7-9`, `components/orders/orders.py:45-51` |
| Image URL construction without a request | `components/catalog/catalog.py:6`, `components/catalog/catalog.py:32-33` |
| Orders to the local settlement fake (development only, used only when `dev` is set) | `components/orders/orders.py:11-12`, `components/orders/orders.py:47` |
| Tools to GitHub through the `gh` CLI | `tools/fanout.sh:10-12`, `tools/fanout.sh:24-29` |

Shapes: rounded = people, rectangle = repository units, cylinder = data store, hexagon = external system. Dashed line = inferred.

## Components

| Component | Kind | Technology | Responsibility | Pages | Size (files, lines, functions, routes) |
| --- | --- | --- | --- | --- | --- |
| `catalog` | Service and library | Python 3 standard library | Product data, price/stock lookups, optional HTTP API | [`catalog`](lld/catalog/README.md), [`endpoints`](lld/api/catalog/catalog.md) | 3 source files, 108 lines, 10 runtime functions, 2 routes |
| `orders` | Library | Python 3 standard library | Totals, stock validation, settlement, optional remote catalog client | [`orders`](lld/orders/README.md) | 4 source files, 158 lines, 18 functions/methods (7 in `orders.py` and `catalog_client.py`, 11 test methods), 0 routes |
| `bible-mode-b` | CLI and workflow component | Python 3 and GitHub Actions | Starts and reconciles analysis runs, assigns sessions, gates work, tracks deltas | [`bible-mode-b`](lld/bible-mode-b/README.md) | 1 Python file of 1,336 lines (74 functions/methods, 2 classes, one more function nested in `Queue.delta`) and 4 workflow files of 201 lines, 0 HTTP routes |
| `tools` | CLI and shell tools | Python 3 and Bash | Component planning, artifact gate, issue fanout | [`tools`](lld/tools/README.md) | 3 files, 210 lines, 7 Python functions, 0 routes |

## Reading paths

| You are | Read, in order |
| --- | --- |
| Manager or new joiner | This page, [`mind map`](00-mind-map.md), [`system context`](hld/01-system-context.md), [`key flows`](hld/05-key-flows.md) |
| Architect | [`HLD 01`](hld/01-system-context.md), [`02`](hld/02-architecture.md), [`03`](hld/03-integrations.md), [`04`](hld/04-data-architecture.md), [`05`](hld/05-key-flows.md), [`06`](hld/06-cross-cutting.md), then each component README under [`lld`](lld/) |
| Engineer changing a component | Its component README, module pages, any catalog endpoint card, and the [`data dictionary`](lld/data-dictionary.md) |
| Operator | [`deployment architecture`](hld/02-architecture.md), [`cross-cutting concerns`](hld/06-cross-cutting.md), and [`configuration`](reference/configuration.md) |

## Files

One line per analysis file, in reading order. Generated inventory, coverage, and knowledge artifacts are included.

- [`00-mind-map.md`](00-mind-map.md)
- [`README.md`](README.md)
- [`hld/01-system-context.md`](hld/01-system-context.md)
- [`hld/02-architecture.md`](hld/02-architecture.md)
- [`hld/03-integrations.md`](hld/03-integrations.md)
- [`hld/04-data-architecture.md`](hld/04-data-architecture.md)
- [`hld/05-key-flows.md`](hld/05-key-flows.md)
- [`hld/06-cross-cutting.md`](hld/06-cross-cutting.md)
- [`reference/glossary.md`](reference/glossary.md)
- [`reference/configuration.md`](reference/configuration.md)
- [`reference/risks-and-surprises.md`](reference/risks-and-surprises.md)
- [`reference/open-questions.md`](reference/open-questions.md)
- [`lld/data-dictionary.md`](lld/data-dictionary.md)
- [`lld/catalog/README.md`](lld/catalog/README.md)
- [`lld/catalog/catalog.md`](lld/catalog/catalog.md)
- [`lld/catalog/service.md`](lld/catalog/service.md)
- [`lld/catalog/test_catalog.md`](lld/catalog/test_catalog.md)
- [`lld/api/catalog/catalog.md`](lld/api/catalog/catalog.md)
- [`lld/orders/README.md`](lld/orders/README.md)
- [`lld/orders/orders.md`](lld/orders/orders.md)
- [`lld/orders/catalog_client.md`](lld/orders/catalog_client.md)
- [`lld/orders/test_catalog_client.md`](lld/orders/test_catalog_client.md)
- [`lld/orders/test_orders.md`](lld/orders/test_orders.md)
- [`lld/bible-mode-b/README.md`](lld/bible-mode-b/README.md)
- [`lld/bible-mode-b/bible_queue.md`](lld/bible-mode-b/bible_queue.md)
- [`lld/tools/README.md`](lld/tools/README.md)
- [`lld/tools/plan.md`](lld/tools/plan.md)
- [`lld/tools/gate.md`](lld/tools/gate.md)
- [`lld/tools/fanout.md`](lld/tools/fanout.md)
- [`ledger/coverage-ledger.md`](ledger/coverage-ledger.md)
- [`ledger/coverage-report.md`](ledger/coverage-report.md)
- [`ledger/baseline.json`](ledger/baseline.json)
- [`ledger/citations.tsv`](ledger/citations.tsv)
- [`ledger/inventory.json`](ledger/inventory.json)
- [`ledger/symbol-checklist.md`](ledger/symbol-checklist.md)
- [`ledger/issues/plan.md`](ledger/issues/plan.md)
- [`ledger/issues/catalog.md`](ledger/issues/catalog.md)
- [`ledger/issues/orders.md`](ledger/issues/orders.md)
- [`ledger/issues/bible-mode-b.md`](ledger/issues/bible-mode-b.md)
- [`ledger/issues/tools.md`](ledger/issues/tools.md)
- [`ledger/issues/assemble.md`](ledger/issues/assemble.md)
- [`ledger/components/catalog/status.json`](ledger/components/catalog/status.json)
- [`ledger/components/catalog/verification-coverage.md`](ledger/components/catalog/verification-coverage.md)
- [`ledger/components/catalog/verification-report.md`](ledger/components/catalog/verification-report.md)
- [`ledger/components/catalog/verification-report-2026-11-23.md`](ledger/components/catalog/verification-report-2026-11-23.md)
- [`ledger/components/catalog/verification-report-2026-11-23-2.md`](ledger/components/catalog/verification-report-2026-11-23-2.md)
- [`ledger/components/orders/status.json`](ledger/components/orders/status.json)
- [`ledger/components/orders/verification-coverage.md`](ledger/components/orders/verification-coverage.md)
- [`ledger/components/orders/verification-report.md`](ledger/components/orders/verification-report.md)
- [`ledger/components/orders/verification-report-2026-11-23.md`](ledger/components/orders/verification-report-2026-11-23.md)
- [`ledger/components/orders/questions.md`](ledger/components/orders/questions.md)
- [`ledger/components/tools/status.json`](ledger/components/tools/status.json)
- [`ledger/components/tools/verification-coverage.md`](ledger/components/tools/verification-coverage.md)
- [`ledger/components/tools/verification-report.md`](ledger/components/tools/verification-report.md)
- [`ledger/components/tools/verification-report-2026-11-23.md`](ledger/components/tools/verification-report-2026-11-23.md)
- [`ledger/components/tools/questions.md`](ledger/components/tools/questions.md)
- [`ledger/components/bible-mode-b/status.json`](ledger/components/bible-mode-b/status.json)
- [`ledger/components/bible-mode-b/verification-coverage.md`](ledger/components/bible-mode-b/verification-coverage.md)
- [`ledger/components/bible-mode-b/verification-report.md`](ledger/components/bible-mode-b/verification-report.md)
- [`ledger/components/bible-mode-b/verification-report-2026-11-23.md`](ledger/components/bible-mode-b/verification-report-2026-11-23.md)
- [`ledger/components/bible-mode-b/verification-report-2026-11-23-2.md`](ledger/components/bible-mode-b/verification-report-2026-11-23-2.md)
- [`ledger/components/bible-mode-b/verification-report-2026-11-23-3.md`](ledger/components/bible-mode-b/verification-report-2026-11-23-3.md)
- [`ledger/components/bible-mode-b/verification-report-2026-11-23-4.md`](ledger/components/bible-mode-b/verification-report-2026-11-23-4.md)
- [`ledger/components/bible-mode-b/verification-report-2026-11-23-5.md`](ledger/components/bible-mode-b/verification-report-2026-11-23-5.md)
- [`progress.md`](progress.md)
- [`run-notes.md`](run-notes.md)
- [`knowledge/AGENT-CONTEXT.md`](knowledge/AGENT-CONTEXT.md)
- [`knowledge/README.md`](knowledge/README.md)
- [`knowledge/graph.json`](knowledge/graph.json)
- [`knowledge/nodes.csv`](knowledge/nodes.csv)
- [`knowledge/edges.csv`](knowledge/edges.csv)
- [`knowledge/chunks.jsonl`](knowledge/chunks.jsonl)
- [`knowledge/symbol-index.json`](knowledge/symbol-index.json)
- [`components.json`](components.json)
- [`components.md`](components.md)
- [`ledger/next.md`](ledger/next.md)
- [`ledger/session.json`](ledger/session.json)
- [`status.json`](status.json)

## Totals

| Measure | Count |
| --- | --- |
| Components / source files / current source lines | 4 / 14 (11 hold code, 3 are empty `__init__.py` files) / 1,812 |
| Symbols documented / functions with full cards | 116 / 98 |
| Routes documented | 2 catalog GET endpoints (the static scanner finds 0) |
| External nodes / named graph stores | 6 / 1; the data dictionary describes 3 stores and no relational tables |
| Flows / Mermaid diagrams | 10 end-to-end flows / 44 diagrams (43 without the generated `components.md`) |
| Business rules | 27 |
| Statements marked inferred / assumed | 30 / 1 |
| Risks and surprises / unanswered questions | 13 / 0 |
| Knowledge graph nodes / edges / chunks | 211 / 566 / 323 |

<!-- cites .github/bible/bible_queue.py@5886e8a4b1928e02dee435ffad7e6f9a1e5ec075 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/bible-queue.yml@d54080b12d039672f31f0d0924cc380ded069010 -->

<!-- cites README.md@62b6ccb3c5858e5b699500d9253942283b61da60 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/service.py@64e5abbab5e101fac6e56c67450ac4c6346198f1 -->

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
