# Revision log

Applied from `verification-report.md`, fingerprint `c2be3c0916a66a73`, of 2026-11-23, verdict `PASS AFTER CORRECTIONS`.

| Item | Location | What was done | Evidence checked | Agrees with the report? |
| --- | --- | --- | --- | --- |
| V-001 | `lld/bible-mode-b/bible_queue.md`, `lld/bible-mode-b/README.md`, HLD and knowledge citations | Re-read the changed queue source, shifted stale queue citations to current locations, corrected relevant prose and refreshed the affected cards. | `.github/bible/bible_queue.py:104-1294` | Yes |
| V-002 | `lld/bible-mode-b/bible_queue.md`, `settings_of` | Documented the missing/non-object marker, unsafe analysis path, unsupported depth and unsafe model checks, including their return branches. | `.github/bible/bible_queue.py:378-398` | Yes |
| V-003 | `lld/bible-mode-b/bible_queue.md`, `main`, `Queue.assemble_phase`, `Queue.delta` | Rewrote the affected cards against the current CLI options, settings validation, session orchestration and delta paths. | `.github/bible/bible_queue.py:910-1294` | Yes |
| V-004 | `README.md`, `ledger/coverage-ledger.md` | Replaced the stale PASS figures with the deep gate result: 116/116 symbols, 310/310 branches, 1,860/1,860 citations and 231/231 same-file calls. | `ledger/coverage-report.md` | Yes |
| V-005 | `lld/bible-mode-b/bible_queue.md` | Added the five missing helper/method cards and index/call-graph links, updated the queue line count, cited every branch, and completed the remaining same-file edges. | `.github/bible/bible_queue.py:42-1294`; [coverage report](ledger/coverage-report.md) | Yes |
| V-006 | `reference/configuration.md`, `hld/06-cross-cutting.md`, `lld/data-dictionary.md`, `ledger/coverage-ledger.md` | Described the catalog–orders TLS inventory and certificate plan as planning-only, recorded the manifest and scanner inventory, and added their four files to the ledger. | `tls-migration/01-inventory.md:1-36`; `tls-migration/02-certificate-plan.md:1-53`; `tls-migration/tls-services.yaml:1-49`; `tls-migration/evidence/inventory.json:1-292` | Yes |
| V-007 | `lld/data-dictionary.md`, `knowledge/AGENT-CONTEXT.md` | Narrowed the component catalog and status entries to fields the queue actually reads and cited the in-scope consumer code. The resolved open-questions statement already cites the code paths supporting its answers. | `.github/bible/bible_queue.py:490-623,681-793,831-844`; `components/orders/orders.py:5,19-20,35-42`; `components/orders/catalog_client.py:1-4,19-23`; `tools/fanout.sh:13-15` | Yes; unsupported artifact-generation details were not retained as queue contracts. |
| N-01 | `verification-report-2026-11-23.md` | Rechecked and corrected four source-line citations marked by the delta queue. This dated archive was updated; the active `verification-report.md` was not edited. | `.github/bible/bible_queue.py:149-154,169-173,241-244,378-398,1127-1165,1244-1290` | Yes |
| N-02 | `lld/bible-mode-b/bible_queue.md` | Clarified that `report_facts` uppercases the verdict but returns the captured fingerprint unchanged, and corrected the `age` caller list. The separate module structure summary now assigns evidence to the API client, helpers, queue, and CLI clauses separately. | `.github/bible/bible_queue.py:454-455,496,500,1147,1187,1244-1294` | Yes |
| N-03 | `lld/catalog/service.md` | Replaced shortened source filenames with the full source path in the catalog service branch rows. | `components/catalog/service.py:24-34` | Yes |
| N-04 | `README.md`, HLD and component diagrams | Added protocol, scheme, and applicable port labels to network edges and replaced Mermaid-disallowed punctuation. The image CDN remains explicitly a constructed URL target, not a request. | `.github/bible/bible_queue.py:110-119`; `components/catalog/catalog.py:36-39`; `components/orders/orders.py:7-12,45-50`; [diagram pages](README.md) | Yes |
| N-05 | `lld/orders/README.md`, `revision-log.md` | Replaced analysis-output path-and-line citations, which the source coverage resolver cannot resolve, with links to the recorded answer and coverage report; the supported implementation facts retain source citations. | `components/orders/orders.py:5,19-20,35-42`; `components/orders/catalog_client.py:1-4,11,14-23`; `components/orders/test_catalog_client.py:37-62`; [coverage report](ledger/coverage-report.md) | Yes |
| N-06 | `lld/bible-mode-b/bible_queue.md` | Corrected the source line count, documented the case-insensitive fingerprint match and unchanged captured value, and included the module guard in the CLI structure summary. | `.github/bible/bible_queue.py:454-455,1244-1294` | Yes |

## Statements added

- The TLS migration is planning-only, with `migrator_model: null` and producer stage `0`; no TLS runtime behavior is claimed.
- The queue-consumed component catalog contract is limited to `proposed`, `components`, component `name`, and `est_sessions`.

## Statements corrected

- Queue citations, cards, branch rows, call-graph edges, component size and front-page coverage figures now match the current source and deep coverage report.
- TLS migration files are listed in the coverage ledger and described only as plans and scan evidence.

## Statements withdrawn

- Catalog JSON generator fields not consumed or validated by the queue were removed from the queue data contract.

## Questions closed or narrowed

None.

## Items not applied, with the reason

None.
