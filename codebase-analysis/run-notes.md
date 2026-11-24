# Run notes

## Pass 6 — Assistant-related text

The assistant-related search matched terminology and operational task text, not instructions for this analysis session. No hit asked the reader to override prior instructions or reveal protected information. The matched task text is recorded here as repository data:

- `.github/workflows/poc-assign-copilot.yml:17-23`, `.github/workflows/poc-assign-copilot.yml:39`, `.github/workflows/poc-assign-copilot.yml:72` — workflow inputs and the default task ask Copilot to create one documentation file; the workflow passes that task through the created issue. The behavior is described in `lld/bible-mode-b/README.md`.
- `.github/bible/bible_queue.py:2-38`, `.github/bible/bible_queue.py:60-70`, `.github/bible/bible_queue.py:92-105`, `.github/bible/bible_queue.py:579-580`, `.github/bible/bible_queue.py:591-594`, `.github/bible/bible_queue.py:676-678`, `.github/bible/bible_queue.py:811-817`, `.github/bible/bible_queue.py:1143-1149`, `.github/bible/bible_queue.py:1183-1187`, `.github/bible/bible_queue.py:1198-1206`, `.github/bible/bible_queue.py:1273-1281` — module documentation, agent identities, labels, and the issue and comment text the queue writes for Copilot (plan, verification, revision, continuation, update, hold and retry messages). These are queue behavior, not instructions to this session. (Line numbers re-checked against the 1,336-line file on 24 Nov 2026.)
- `.github/workflows/bible-plan.yml:15` and `.github/workflows/bible-delta.yml:2` — model description and workflow comment.
- `tools/fanout.sh:2`, `tools/fanout.sh:4` — controller comments describing issue assignment.
- `tools/plan.py:1` — module docstring noting that inventory is deterministic and uses no LLM.
- `README.md:3`, `README.md:5-6` — repository description and skill/workflow inventory.

The matching lines are documented as component behavior; they were not treated as directions for this analysis.

## Revision of the report of 2026-11-24, round 4: judgments made without the user

- The report's "README's cautions" (item V-017, the catalog binds loopback by default) was read as the catalog component README, the page that has the cautions about the server; the front page has no cautions section.
- The bind rule for an empty `CATALOG_HOST` is written as `(assumed: library behaviour)`: the code does not show what an empty host string binds. The report states it as fact.
- Two corrections were applied in a wider scope than the report names: the narrowing of "POST" for the settlement request (R4-V-007) and the bind rule of `make_server` on every page that repeated it (R4-V-009). Both are in `revision-log.md`.
- `(inferred: ...)` was used for statements that rest on a search or a comment; where the statement rests on library behaviour, `(assumed: ...)` was used. The marks are counted on the front page by searching the pages, not by reading the gate.
- The queue file did not change, so there was no delta to apply and the line numbers of the report were valid; each cited line was still opened before it was used.
- One command of this session created an empty file `/tmp/_unused` outside the analysis folder by mistake (a stray `cat >` redirect) and removed it in the next command. Nothing else was written outside the folder, and nothing was run, installed or fetched over a network.

<!-- cites .github/bible/bible_queue.py@5886e8a4b1928e02dee435ffad7e6f9a1e5ec075 -->

<!-- cites .github/workflows/bible-delta.yml@5317a1ada61df3db98cc21d8db6d1415fe732c58 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/poc-assign-copilot.yml@dab60e0d846bfee50726dce662df48fc186ca3d3 -->

<!-- cites README.md@62b6ccb3c5858e5b699500d9253942283b61da60 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
