---
id: reference/open-questions
kind: reference
source: [codebase-analysis/ledger/components/orders/questions.md, codebase-analysis/ledger/components/tools/questions.md]
summary: Lists the answered component questions and confirms that none remain open
depends_on: [page:hld/02-architecture.md, page:lld/orders/README.md, page:lld/tools/README.md]
---
# Open questions

No unanswered questions remain from the component analyses. The questions below were answered and are retained so later readers can find the decisions.

| # | Question | Why it matters | Where I looked | Who could answer |
| --- | --- | --- | --- | --- |
| Q-001, resolved | Is the catalog HTTP client for separately deployed orders or should direct import be the only path? **Answer:** Both paths are intentional; direct imports are used in today's in-process mode, and the HTTP client is for separate-service mode, with tests as its only current repository callers. | Preserves both intentional access modes and avoids mistaking the test-only HTTP path for current deployment. | `components/orders/orders.py:5`, `components/orders/orders.py:19-20`, `components/orders/orders.py:35-42`; `components/orders/catalog_client.py:1-4`, `components/orders/catalog_client.py:19-23`; `components/orders/test_catalog_client.py:37-62` | Repository person, answered |
| Q-002, resolved | Is the `component-analysis` skill path in fanout intentional? **Answer:** No; it is a stale reference from an earlier experiment. Do not change the script; document the stale path. | Prevents generated instructions from being mistaken for a repository skill or silently “fixed” against the answered decision. | `tools/fanout.sh:13-15` | Repository person, answered |

<!-- cites components/orders/catalog_client.py@469f9d282aab983cdd85f364e46bcd02ef6d3635 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->
