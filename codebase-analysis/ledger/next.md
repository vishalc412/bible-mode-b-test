```text
NEXT PASS 2: components and plan
Write progress.md with a '## Components' section (references/passes.md, Pass 2). Suggested split by top folder:
  - components: 7 source files, 7 packets, 0 routes
  - .github: 1 source files, 4 packets, 0 routes
  - tools: 3 source files, 3 packets, 0 routes
Total packets: 14. Split a large folder into the areas its routes, packages and services show.
Then run discover.py, which checks the plan and writes the component catalog and its table:
  python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/discover.py --repo . --analysis codebase-analysis
Show its table to the user once and ask: which components (names, or all)? For one component, continue with
next.py --component NAME. For all of them in this chat, run next.py again: it hands you packets in priority order.
```
