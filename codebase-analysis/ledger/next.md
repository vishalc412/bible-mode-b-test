```text
NEXT DELTA recheck codebase-analysis/hld/05-key-flows.md (23 citations waiting in 5 pages)

Each line below cites code that changed. Open the code, correct the citation and the sentence it supports, then delete the marker:
  - line 62: | 4 | Queue ensures labels and creates a tracker issue with settings in a hidden JSON comment. | `.github/bible/bible_queue.py:828-854` <!-- recheck: was .github/bible/bible_queue.py:828-854 --> |
  - line 67: **Failure paths:** A non-default branch skips the job; missing secret exits with an error; invalid models, components, missing repository/token settings, or an already-open tracker terminate `start` r
  - line 135: | 1 | Agent opens a chunk PR containing component pages and a status artifact. | `.github/bible/bible_queue.py:659-696` <!-- recheck: was .github/bible/bible_queue.py:659-696 --> |
  - line 136: | 2 | Queue validates changed paths and reads status JSON at the PR head. | `.github/bible/bible_queue.py:659-697` <!-- recheck: was .github/bible/bible_queue.py:659-697 --> |

Then run next.py again.
```
