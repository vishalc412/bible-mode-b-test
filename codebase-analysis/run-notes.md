# Run notes

## Pass 6 — Assistant-related text

The assistant-related search matched terminology and operational task text, not instructions for this analysis session. No hit asked the reader to override prior instructions or reveal protected information. The matched task text is recorded here as repository data:

- `.github/workflows/poc-assign-copilot.yml:17-23,39,72` — workflow inputs and the default task ask Copilot to create one documentation file; the workflow passes that task through the created issue. The behavior is described in `lld/bible-mode-b/README.md`.
- `.github/bible/bible_queue.py:2-38,60-70,92-105,579-580,591-594,676-678,811-817,1143-1149,1183-1187,1198-1206,1273-1281` — module documentation, agent identities, labels, and the issue and comment text the queue writes for Copilot (plan, verification, revision, continuation, update, hold and retry messages). These are queue behavior, not instructions to this session. (Line numbers re-checked against the 1,336-line file on 24 Nov 2026.)
- `.github/workflows/bible-plan.yml:15` and `.github/workflows/bible-delta.yml:2` — model description and workflow comment.
- `tools/fanout.sh:2,4` — controller comments describing issue assignment.
- `tools/plan.py:1` — module docstring noting that inventory is deterministic and uses no LLM.
- `README.md:3,5-6` — repository description and skill/workflow inventory.

The matching lines are documented as component behavior; they were not treated as directions for this analysis.

<!-- cites .github/workflows/bible-delta.yml@5317a1ada61df3db98cc21d8db6d1415fe732c58 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
