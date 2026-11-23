```text
NEXT PACKET 4 of 4 (3 done, 75%; 3 in this chat, budget 6)
Component: bible-mode-b
Read:      .github/bible/bible_queue.py lines 797-844 (of 844), in full
Write:     codebase-analysis/lld/bible-mode-b/bible_queue.md (extend)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (1):
  - card `main` (function, lines 797-840) - branch lines to cite: 814, 815, 819, 820, 821, 823, 824, 826, 827, 833, 839, 840; calls: `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `gh.ensure_labels`, `gh.issues`, `gh.create_issue`, `print`, `n.strip`, `any`, `queue.reconcile`, `queue.delta`, `str` and 7 more (ledger/symbol-checklist.md); stamp `<!-- code: f407f91f47e7 -->`: not named on the page

When every item is written, write one line to the user, and run next.py again.
Write only under lld/bible-mode-b/, lld/api/bible-mode-b/ and ledger/components/bible-mode-b/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component bible-mode-b
```
