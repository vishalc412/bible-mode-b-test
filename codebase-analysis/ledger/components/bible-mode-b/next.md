```text
NEXT PACKET 3 of 3 (2 done, 66%; 1 in this chat, budget 6)
Component: bible-mode-b
Read:      .github/bible/bible_queue.py lines 644-848 (of 848), in full
Write:     codebase-analysis/lld/bible-mode-b/README.md (extend)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (6):
  - card `Queue.follow` (method, lines 644-696) - branch lines to cite: 646, 648, 650, 653, 655, 656, 659, 666, 668, 670, 671, 672, 679, 681, 683, 686, 687, 689, 690, 692; calls: `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `gh.pr_files`, `().startswith`, `f.startswith`, `os.path.basename`, `join`, `status_of`, `as_int`, `status.get`, `().get`, `gh.file`, `gh.label`, `issue.get`, `any`, `gh.merge`, `gh.unlabel`, `gh.close`; stamp `<!-- code: baf0608fa459 -->`: the code changed since the card was written: rewrite it and replace its stamp
  - card `Queue.check` (method, lines 698-715) - branch lines to cite: 701; calls: `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `shutil.rmtree`, `os.path.abspath`, `self.settings.get`, `printed.stdout.strip`, `().splitlines`, `run.stdout.strip`; stamp `<!-- code: 4357020a3cd5 -->`: branch lines not in its Branches and errors table: 701
  - card `Queue.assemble_phase` (method, lines 717-757) - branch lines to cite: 719, 722, 725, 729, 730, 732, 734, 737, 740, 743, 745, 746; calls: `any`, `self.run_issues`, `gh.create_issue`, `settings.get`, `self.held`, `self.session`, `issue_text`, `assignment`, `gh.close`, `self.hold_start_error`, `self.fail_or_retry`, `i.get`, `gh.linked_prs`, `report_facts`, `p.get`, `gh.is_agent_pr`, `gh.file`, `get`, `gh.comment`; stamp `<!-- code: 73a196189485 -->`: branch lines not in its Branches and errors table: 719, 722, 729, 732, 734, 737, 740, 743, 745, 746
  - card `Queue.render` (method, lines 759-769) - branch lines to cite: 766, 768; calls: `rows.items`, `().isoformat`, `json.dumps`, `now`, `join`, `self.gh.set_body`, `body.split`, `split`, `tracker.get`, `self.log`; stamp `<!-- code: 651906b39ffd -->`: branch lines not in its Branches and errors table: 766, 768
  - card `Queue.delta` (method, lines 772-798) - branch lines to cite: 776, 784, 786; calls: `gh.default_branch`, `json_file`, `self.log`, `gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `sorted`, `().values`, `components.component_map`, `p.startswith`, `gh.issues`, `gh.create_issue`, `assignment`, `comp_label`, `join`, `len`, `components.assign`; stamp `<!-- code: 173a0090e878 -->`: branch lines not in its Branches and errors table: 776, 784, 786
  - card `main` (function, lines 801-844) - branch lines to cite: 818, 819, 823, 824, 825, 827, 828, 830, 831, 837, 843, 844; calls: `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `gh.ensure_labels`, `gh.issues`, `gh.create_issue`, `print`, `n.strip`, `any`, `queue.reconcile`, `queue.delta`, `str` and 7 more (ledger/symbol-checklist.md); stamp `<!-- code: f407f91f47e7 -->`: branch lines not in its Branches and errors table: 818, 825, 828, 830, 831, 837, 843, 844

When every item is written, write one line to the user, and run next.py again.
Write only under lld/bible-mode-b/, lld/api/bible-mode-b/ and ledger/components/bible-mode-b/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I .github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component bible-mode-b
```
