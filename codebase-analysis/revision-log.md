# Revision log

Applied from verification-report.md, fingerprint c2be3c0916a66a73, of 2026-11-23, verdict PASS AFTER CORRECTIONS.

| Item | Location | What was done | Code re-opened | Agrees with the report? |
| --- | --- | --- | --- | --- |
| V-001 | Queue citations in the queue LLD, component README, key flows, configuration and data dictionary | Rechecked stale queue citations against the refreshed source and replaced them with current evidence. | Yes | Yes |
| V-002 | `lld/bible-mode-b/bible_queue.md` index and call graph | Added cards for `shown_files`, `Queue.could_not_check`, `Queue.whole_fingerprint`, `Queue.deferred_updates` and `Queue.whole_hold`; connected them to their callers. | Yes | Yes |
| V-003 | `lld/bible-mode-b/bible_queue.md`, `Queue.render` | Rewrote the card to document the hidden `bible-state` block and current body update behavior. | Yes | Yes |
| V-004 | `README.md` coverage status | Replaced the stale pass claim with the refreshed deep-gate results and corrected-after-verification status. | Yes | Yes |
| V-005 | Queue LLD index, cards and call graph | Updated source line counts and function index; documented current branch lines and same-file calls for the changed queue functions. | Yes | Yes |
| V-006 | `lld/bible-mode-b/bible_queue.md`, `GitHub` | Corrected the `GitHub` citation to its current field initialization at lines 104-108. | Yes | Yes |
| V-007 | `ledger/coverage-ledger.md` | Added the four in-scope `tls-migration/` files and corrected the inventory snapshot to 24 files. | Yes | Yes |
| N-01 | Whole-analysis coverage and inventory | Refreshed inventory and reran the deep coverage gate; results are recorded in the ledger and progress page. | Yes | — |
| N-02 | Depth, diagrams, evidence and knowledge-base checks | Rechecked changed queue cards and their dependent pages; the revised analysis remains unverified pending a separate verification. | Yes | — |
| V-001 (completion, 24 Nov 2026) | Every citation of `.github/bible/bible_queue.py` on pages other than the verifier's records: `lld/bible-mode-b/bible_queue.md` (785 citations), `lld/bible-mode-b/README.md` (140), `hld/01` to `hld/06` (86), `lld/data-dictionary.md` (45), `reference/configuration.md` (16), `reference/glossary.md` (8), `reference/risks-and-surprises.md` (6), `knowledge/AGENT-CONTEXT.md` (30), `README.md` (4), `ledger/coverage-ledger.md` (1) | The first pass re-cited only the card Source lines and the cards that the delta touched. This pass opened the cited lines of all 1,121 citations in the current 1,310-line file. About 220 citations on the non-card pages were re-numbered (they still counted lines of the 867- and 1,130-line versions), the Called by rows of 36 cards were regenerated from the code, and the Steps citations of `Queue.hold_start_error`, `Queue.fail_or_retry` and `Queue.check` were moved. Three statements were corrected: the subprocesses of `Queue.check` do have a 300-second timeout (`GATE_TIMEOUT`, `hld/03-integrations.md` and the component README said none), the Called by row of `age` named the wrong callers, and the page line counts and function count (1,310 and 74) were stale. | Yes | Yes |

## Statements added

The five newly discovered queue helpers are indexed and carded. The queue's current `render` behavior includes a hidden `bible-state` marker containing `self.state`.

## Statements corrected

Queue source line ranges, card branches and citations were refreshed against `.github/bible/bible_queue.py`; coverage counts and the source line count reflect the regenerated inventory and gate.

## Statements withdrawn

The previous claim that deep coverage passed with 111/111 symbols and 274/274 branch lines is withdrawn.

## Questions closed or narrowed

None.

## Items not applied, with the reason

None.
