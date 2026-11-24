```text
NEXT DELTA: the code changed since the analysis last matched it
Run: python3 -I .github/skills/analyzing-a-codebase/scripts/delta.py --repo . --analysis codebase-analysis --depth deep --apply
(or tracking-codebase-changes' track.py --apply when the repository has a .git folder)
It moves each citation from the version its page or card was written against, marks the rest for a recheck and records the work.
Then run next.py again: it hands that work out file by file.
```
