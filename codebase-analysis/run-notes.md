# Run notes

## Pass 6 — Assistant-related text

The assistant-related search matched terminology and operational task text, not instructions for this analysis session. No hit asked the reader to override prior instructions or reveal protected information. The matched task text is recorded here as repository data:

- `.github/workflows/poc-assign-copilot.yml:17-23`, `.github/workflows/poc-assign-copilot.yml:39`, `.github/workflows/poc-assign-copilot.yml:72` — workflow inputs and the default task ask Copilot to create one documentation file; the workflow passes that task through the created issue. The behavior is described in `lld/bible-mode-b/README.md`.
- `.github/bible/bible_queue.py:2-38`, `.github/bible/bible_queue.py:60-70`, `.github/bible/bible_queue.py:92-106`, `.github/bible/bible_queue.py:510-513`, `.github/bible/bible_queue.py:639-640`, `.github/bible/bible_queue.py:651-654`, `.github/bible/bible_queue.py:764-766`, `.github/bible/bible_queue.py:900-908`, `.github/bible/bible_queue.py:1122-1124`, `.github/bible/bible_queue.py:1241-1247`, `.github/bible/bible_queue.py:1281-1285`, `.github/bible/bible_queue.py:1296-1304`, `.github/bible/bible_queue.py:1371-1379` — module documentation, agent identities, labels, and the issue and comment text the queue writes for Copilot (plan, verification, revision, continuation, update, hold and retry messages). These are queue behavior, not instructions to this session. (Line numbers re-checked against the 1,434-line file on 24 Nov 2026, after the update for the supplier-feed HTTPS change and the queue's re-check and replay changes.)
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

## Revision of the report of 2026-11-24, round 5: judgments made without the user

- The report's closing words for the replay sentence, "or a person picks them up", were not written: no code line says so. The sentence says what the code shows, that the next update issue for the same component asks for every change since the baseline.
- `(inferred: ...)` was used for absences and searches, `(assumed: ...)` for library or GitHub behaviour that the code only states in a comment or relies on. The counts of the marks on the front page are a search of the pages; the log and these notes are not counted.
- The gate does not resolve paths under `.github/skills` (outside the inventory), so the `NEW_CHAT` row of the data dictionary names the toolkit's `next.py` in words instead of citing its lines.
- Two diagrams were added in hld/04 (the component row on the tracker, and the data model of the hidden `bible-settings` and `bible-state` blocks) and two stores were drawn in the containers diagram, because the report names the omissions; their statements are new and are listed in `revision-log.md` (R5-V-015) for the re-check.
- Two slips of this session against the instructions: one command ran `git diff --stat` (read-only, it changed nothing) and one command created an empty file `/tmp/NOPE` outside the analysis folder by mistake and removed it in the next command. Nothing else was written outside the folder, and nothing was installed or fetched over a network.

## Revision of the report of 2026-11-24, round 6: judgments made without the user

- The sweep (R6-S-01) counts sentences, table cells and list items, not search hits. A sentence that only reports what a docstring or comment says, and cites that line ("its docstring says it runs nightly from cron"), was left; one that states the behaviour the comment describes got a mark. The `revision-log.md`, `run-notes.md`, `delta-log.md` and `progress.md` pages, the reports and the ledger were not swept; the generated pages (`components.md`, `knowledge/README.md`, the knowledge tables) were read, not edited.
- The hit counts in the marks are from searches run in this session over the files outside `codebase-analysis/` and `.github/skills/` (24 files), or over the directories the mark names. A search of a word list counts lines that match, as `grep` prints them.
- Where one sentence rests on a search and on platform behaviour, one parenthesis holds both (`inferred: ...; assumed: ...`), the form the report accepted for `bible_queue.md`, line 1092 and `plan.md`, line 154.
- The user's answer to Q1 and Q-002 is named in the sentence as "the recorded answer ... a user decision" where the sentence says what is "intentional" or "today's deployment"; it is not stated as a fact the code shows.
- Names of outside systems in the front matter were merged to `external:GitHub`, `external:Payment partner` and `external:Local settle fake` so that the graph has one node per system (5 external nodes, was 6).
- A diagram nit not asked for (the hidden-block ER diagram had no key column) was fixed because the quality gate's D5 names it.
- The report's V-013 item 11 names flow 9 among the diagrams with renamed aliases; its aliases are the real file names, so only flow 7 and `lld/api/catalog/catalog.md` were changed.
- Two commands of this session redirected output to `/dev/null` (no file was created). No other file was written outside `codebase-analysis/`; git, `gh` and every network command were not run; nothing was installed. Python ran as `python3 -I -B`.

<!-- cites .github/bible/bible_queue.py@a625b4c3353b1744b965b8bbee13e6b3ed5f72a6 -->

<!-- cites .github/workflows/bible-delta.yml@5317a1ada61df3db98cc21d8db6d1415fe732c58 -->

<!-- cites .github/workflows/bible-plan.yml@65016c0e6616ef12f74a26e6d6a4a5f566b584c1 -->

<!-- cites .github/workflows/poc-assign-copilot.yml@dab60e0d846bfee50726dce662df48fc186ca3d3 -->

<!-- cites README.md@62b6ccb3c5858e5b699500d9253942283b61da60 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
