# Delta since the analysis last matched the code

Baseline recorded 2026-11-24T20:00:32 (claude/update-125-126). Applied on 2026-11-24T20:00:32 (claude/update-125-126).

| Measure | Count |
| --- | --- |
| Files changed | 3 |
| Files added | 6 |
| Files removed | 0 |
| Files renamed | 0 |
| Functions changed | 7 |
| Functions added | 8 |
| Functions removed | 0 |
| Functions only moved | 77 |
| Routes added, removed | 0, 0 |
| Citations moved to new lines | 1168 |
| Card citations moved with their code (found by stamp) | 511 |
| Citations marked for a recheck | 253 |
| Work items open | 10 |

## Files added (next.py hands these out as packets)

- `https-migration/changed-files.txt`
- `https-migration/https-allowlist.txt`
- `https-migration/https-inventory.md`
- `https-migration/https-migration-summary.md`
- `https-migration/tests-after.txt`
- `https-migration/tests-before.txt`

## Changed files

| File | Changed | Added | Removed | Only moved |
| --- | --- | --- | --- | --- |
| `.github/bible/bible_queue.py` | `report_facts`, `Queue`, `Queue.reconcile`, `Queue.component`, `Queue.assemble_phase` | `recheck_due`, `accepted`, `Queue.replay_closed_runs`, `Queue.replayed` | - | 71 |
| `components/catalog/catalog.py` | `fetch_supplier_feed` | `NoHTTPRedirectHandler`, `NoHTTPRedirectHandler.redirect_request` | - | 5 |
| `components/catalog/test_catalog.py` | `CatalogTest` | `CatalogTest.test_supplier_feed_uses_verified_https`, `CatalogTest.test_supplier_feed_rejects_redirect_to_http` | - | 1 |

## Work for the analysis

- card `.github/bible/bible_queue.py` Queue.component
- card `.github/bible/bible_queue.py` Queue.assemble_phase
- card `.github/bible/bible_queue.py` Queue.reconcile
- card `.github/bible/bible_queue.py` report_facts
- card `.github/bible/bible_queue.py` recheck_due
- card `.github/bible/bible_queue.py` accepted
- card `.github/bible/bible_queue.py` Queue.replay_closed_runs
- card `.github/bible/bible_queue.py` Queue.replayed
- card `components/catalog/catalog.py` fetch_supplier_feed
- card `components/catalog/catalog.py` NoHTTPRedirectHandler.redirect_request

## Citations waiting for a recheck (212)

- README.md:23
- README.md:27
- README.md:62
- README.md:65
- hld/01-system-context.md:23
- hld/01-system-context.md:58
- hld/01-system-context.md:59
- hld/01-system-context.md:62
- hld/02-architecture.md:78
- hld/02-architecture.md:136
- hld/02-architecture.md:151
- hld/03-integrations.md:42
- hld/03-integrations.md:60
- hld/04-data-architecture.md:21
- hld/04-data-architecture.md:23
- hld/04-data-architecture.md:26
- hld/04-data-architecture.md:32
- hld/04-data-architecture.md:143
- hld/04-data-architecture.md:190
- hld/04-data-architecture.md:222
- hld/04-data-architecture.md:225
- hld/04-data-architecture.md:235
- hld/04-data-architecture.md:239
- hld/05-key-flows.md:170
- hld/05-key-flows.md:172
- hld/05-key-flows.md:173
- hld/05-key-flows.md:176
- hld/05-key-flows.md:238
- hld/05-key-flows.md:239
- hld/05-key-flows.md:241
- hld/05-key-flows.md:242
- hld/05-key-flows.md:244
- hld/05-key-flows.md:245
- hld/05-key-flows.md:289
- hld/06-cross-cutting.md:43
- hld/06-cross-cutting.md:54
- hld/06-cross-cutting.md:62
- hld/06-cross-cutting.md:66
- hld/06-cross-cutting.md:71
- hld/06-cross-cutting.md:105
- knowledge/AGENT-CONTEXT.md:9
- knowledge/AGENT-CONTEXT.md:36
- knowledge/AGENT-CONTEXT.md:45
- knowledge/AGENT-CONTEXT.md:46
- knowledge/AGENT-CONTEXT.md:77
- knowledge/AGENT-CONTEXT.md:88
- knowledge/AGENT-CONTEXT.md:90
- knowledge/AGENT-CONTEXT.md:98
- knowledge/AGENT-CONTEXT.md:102
- knowledge/AGENT-CONTEXT.md:104
- knowledge/AGENT-CONTEXT.md:107
- ledger/coverage-ledger.md:43
- lld/bible-mode-b/README.md:23
- lld/bible-mode-b/README.md:28
- lld/bible-mode-b/README.md:177
- lld/bible-mode-b/README.md:178
- lld/bible-mode-b/README.md:179
- lld/bible-mode-b/README.md:180
- lld/bible-mode-b/README.md:182
- lld/bible-mode-b/README.md:228
- lld/bible-mode-b/README.md:253
- lld/bible-mode-b/README.md:256
- lld/bible-mode-b/README.md:258
- lld/bible-mode-b/README.md:259
- lld/bible-mode-b/README.md:282
- lld/bible-mode-b/README.md:309
- lld/bible-mode-b/README.md:343
- lld/bible-mode-b/bible_queue.md:25
- lld/bible-mode-b/bible_queue.md:29
- lld/bible-mode-b/bible_queue.md:814
- lld/bible-mode-b/bible_queue.md:1261
- lld/bible-mode-b/bible_queue.md:1466
- lld/bible-mode-b/bible_queue.md:1745
- lld/bible-mode-b/bible_queue.md:1756
- lld/bible-mode-b/bible_queue.md:1757
- lld/bible-mode-b/bible_queue.md:1758
- lld/bible-mode-b/bible_queue.md:1775
- lld/bible-mode-b/bible_queue.md:1776
- lld/bible-mode-b/bible_queue.md:1777
- lld/bible-mode-b/bible_queue.md:1778
- lld/bible-mode-b/bible_queue.md:1920
- lld/bible-mode-b/bible_queue.md:1931
- lld/bible-mode-b/bible_queue.md:1932
- lld/bible-mode-b/bible_queue.md:1933
- lld/bible-mode-b/bible_queue.md:1934
- lld/bible-mode-b/bible_queue.md:1935
- lld/bible-mode-b/bible_queue.md:1936
- lld/bible-mode-b/bible_queue.md:1966
- lld/bible-mode-b/bible_queue.md:1967
- lld/bible-mode-b/bible_queue.md:1968
- lld/bible-mode-b/bible_queue.md:1969
- lld/bible-mode-b/bible_queue.md:1970
- lld/bible-mode-b/bible_queue.md:1971
- lld/bible-mode-b/bible_queue.md:1972
- lld/bible-mode-b/bible_queue.md:1973
- lld/bible-mode-b/bible_queue.md:1974
- lld/bible-mode-b/bible_queue.md:1975
- lld/bible-mode-b/bible_queue.md:1976
- lld/bible-mode-b/bible_queue.md:1977
- lld/bible-mode-b/bible_queue.md:1978
- lld/bible-mode-b/bible_queue.md:1979
- lld/bible-mode-b/bible_queue.md:1980
- lld/bible-mode-b/bible_queue.md:1981
- lld/bible-mode-b/bible_queue.md:1982
- lld/bible-mode-b/bible_queue.md:1983
- lld/bible-mode-b/bible_queue.md:1984
- lld/bible-mode-b/bible_queue.md:1985
- lld/bible-mode-b/bible_queue.md:1986
- lld/bible-mode-b/bible_queue.md:2161
- lld/bible-mode-b/bible_queue.md:2172
- lld/bible-mode-b/bible_queue.md:2173
- lld/bible-mode-b/bible_queue.md:2174
- lld/bible-mode-b/bible_queue.md:2175
- lld/bible-mode-b/bible_queue.md:2176
- lld/bible-mode-b/bible_queue.md:2177
- lld/bible-mode-b/bible_queue.md:2178
- lld/bible-mode-b/bible_queue.md:2179
- lld/bible-mode-b/bible_queue.md:2215
- lld/bible-mode-b/bible_queue.md:2216
- lld/bible-mode-b/bible_queue.md:2217
- lld/bible-mode-b/bible_queue.md:2218
- lld/bible-mode-b/bible_queue.md:2219
- lld/bible-mode-b/bible_queue.md:2220
- lld/bible-mode-b/bible_queue.md:2221
- lld/bible-mode-b/bible_queue.md:2222
- lld/bible-mode-b/bible_queue.md:2223
- lld/bible-mode-b/bible_queue.md:2224
- lld/bible-mode-b/bible_queue.md:2225
- lld/bible-mode-b/bible_queue.md:2226
- lld/bible-mode-b/bible_queue.md:2227
- lld/bible-mode-b/bible_queue.md:2228
- lld/bible-mode-b/bible_queue.md:2229
- lld/bible-mode-b/bible_queue.md:2230
- lld/bible-mode-b/bible_queue.md:2231
- lld/bible-mode-b/bible_queue.md:2232
- lld/bible-mode-b/bible_queue.md:2233
- lld/bible-mode-b/bible_queue.md:2234
- lld/bible-mode-b/bible_queue.md:2235
- lld/bible-mode-b/bible_queue.md:2236
- lld/bible-mode-b/bible_queue.md:2237
- lld/bible-mode-b/bible_queue.md:2238
- lld/bible-mode-b/bible_queue.md:2239
- lld/bible-mode-b/bible_queue.md:2240
- lld/bible-mode-b/bible_queue.md:2241
- lld/bible-mode-b/bible_queue.md:2242
- lld/bible-mode-b/bible_queue.md:2243
- lld/bible-mode-b/bible_queue.md:2244
- lld/bible-mode-b/bible_queue.md:2245
- lld/bible-mode-b/bible_queue.md:2246
- lld/bible-mode-b/bible_queue.md:2247
- lld/bible-mode-b/bible_queue.md:2248
- lld/bible-mode-b/bible_queue.md:2644
- lld/bible-mode-b/bible_queue.md:2866
- lld/bible-mode-b/bible_queue.md:2895
- lld/bible-mode-b/bible_queue.md:2900
- lld/bible-mode-b/bible_queue.md:2906
- lld/bible-mode-b/bible_queue.md:2907
- lld/bible-mode-b/bible_queue.md:2908
- lld/bible-mode-b/bible_queue.md:2909
- lld/bible-mode-b/bible_queue.md:2910
- lld/bible-mode-b/bible_queue.md:2928
- lld/bible-mode-b/bible_queue.md:2929
- lld/bible-mode-b/bible_queue.md:2930
- lld/bible-mode-b/bible_queue.md:2991
- lld/bible-mode-b/bible_queue.md:2993
- lld/catalog/README.md:21
- lld/catalog/README.md:23
- lld/catalog/README.md:28
- lld/catalog/README.md:63
- lld/catalog/README.md:69
- lld/catalog/README.md:122
- lld/catalog/README.md:128
- lld/catalog/README.md:139
- lld/catalog/README.md:143
- lld/catalog/README.md:147
- lld/catalog/README.md:151
- lld/catalog/README.md:158
- lld/catalog/README.md:159
- lld/catalog/catalog.md:25
- lld/catalog/catalog.md:29
- lld/catalog/catalog.md:194
- lld/catalog/catalog.md:207
- lld/catalog/catalog.md:211
- lld/catalog/catalog.md:212
- lld/catalog/catalog.md:221
- lld/catalog/catalog.md:265
- lld/catalog/catalog.md:269
- lld/catalog/test_catalog.md:24
- lld/catalog/test_catalog.md:25
- lld/catalog/test_catalog.md:29
- lld/catalog/test_catalog.md:51
- lld/data-dictionary.md:55
- lld/data-dictionary.md:115
- lld/data-dictionary.md:135
- lld/data-dictionary.md:136
- lld/data-dictionary.md:139
- lld/data-dictionary.md:146
- lld/data-dictionary.md:161
- lld/data-dictionary.md:172
- lld/data-dictionary.md:187
