```text
DONE
coverage.py: result PASS at depth deep (pass 11, the gate, is done). Now, in this order:
  1. the checks in references/quality-gate.md;
  2. record the code this analysis describes, so later changes are a delta (it adds a cites line to each page): python3 -I .github/skills/analyzing-a-codebase/scripts/delta.py --repo . --analysis codebase-analysis --init --label NAME
  3. knowledge.py, on the final pages: python3 -I .github/skills/analyzing-a-codebase/scripts/knowledge.py --repo . --analysis codebase-analysis
  4. status.py --write, then finish as SKILL.md says (the bible stays unverified until verifying-a-codebase-analysis passes).
```
