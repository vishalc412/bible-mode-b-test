# bible-mode-b-test

A small sample service ("sample-shop": `components/catalog`, `components/orders`, and `tools/`) used to test Mode B of the AI migration toolkit: GitHub workflows that assign the Copilot coding agent to write and verify a cited codebase analysis, one component at a time.

- `.github/skills/`: the toolkit's skills, installed for Copilot.
- `.github/workflows/poc-assign-copilot.yml`: proof of concept (can a workflow assign Copilot?).
- `.github/workflows/bible-*.yml` and `.github/bible/bible_queue.py`: Mode B.
