---
id: reference/open-questions
kind: reference
source: [codebase-analysis/ledger/components/orders/questions.md, codebase-analysis/ledger/components/tools/questions.md]
summary: Lists the answered component questions and confirms that none remain open
depends_on: [hld/02-architecture, lld/orders/README, lld/tools/README]
---
# Closed in revision

No unanswered questions remain from the component analyses. These resolved questions are retained so later readers can find the decisions.

| Question | Answer | Why it matters | Where resolved | Evidence |
| --- | --- | --- | --- | --- |
| Is the catalog HTTP client for separately deployed orders or should direct import be the only path? | Both paths are intentional; direct imports are used in today's in-process mode, and the HTTP client is for separate-service mode, with tests as its only current repository callers. | Preserves both access modes and avoids mistaking the test-only HTTP path for current deployment. | [Orders component README](../lld/orders/README.md) | `components/orders/orders.py:5,19-20,35-42`; `components/orders/catalog_client.py:1-4,19-23`; `components/orders/test_catalog_client.py:37-62` |
| Is the `component-analysis` skill path in fanout intentional? | No; it is a stale reference from an earlier experiment. Do not change the script; document the stale path. | Prevents generated instructions from being mistaken for a repository skill or silently “fixed” against the answered decision. | [Tools component README](../lld/tools/README.md) | `tools/fanout.sh:13-15` |

<!-- cites components/orders/test_catalog_client.py@1d32463e1cdc21bd3eee3bc1b6f31feb8ef40a2d -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->
