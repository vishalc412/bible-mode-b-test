```text
NEXT PACKET 3 of 13 (12 done, 92%; 1 in this chat, budget 6)
Component: bible-mode-b
Read:      .github/bible/bible_queue.py lines 663-867 (of 867), in full
Write:     codebase-analysis/lld/bible-mode-b/README.md (extend)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (6):
  - card `Queue.follow` (method, lines 663-715) - branch lines to cite: 665, 667, 669, 672, 674, 675, 678, 685, 687, 689, 690, 691, 698, 700, 702, 705, 706, 708, 709, 711; calls: `labels_of`, `self.session`, `self.hold_start_error`, `self.fail_or_retry`, `gh.pr_files`, `().startswith`, `f.startswith`, `os.path.basename`, `join`, `status_of`, `as_int`, `status.get`, `().get`, `gh.file`, `gh.label`, `issue.get`, `any`, `gh.merge`, `gh.unlabel`, `gh.close`; stamp `<!-- code: baf0608fa459 -->`: branch lines not in its Branches and errors table: 665, 667, 669, 674, 675, 678, 685, 691, 698, 700, 702, 705, 706, 708, 709, 711
  - card `Queue.check` (method, lines 717-734) - branch lines to cite: 720; calls: `os.path.join`, `os.path.isfile`, `self.log`, `tempfile.mkdtemp`, `self.gh.tarball`, `subprocess.run`, `shutil.rmtree`, `os.path.abspath`, `self.settings.get`, `printed.stdout.strip`, `().splitlines`, `run.stdout.strip`; stamp `<!-- code: 4357020a3cd5 -->`: branch lines not in its Branches and errors table: 720
  - card `Queue.assemble_phase` (method, lines 736-776) - branch lines to cite: 738, 741, 744, 748, 749, 751, 753, 756, 759, 762, 764, 765; calls: `any`, `self.run_issues`, `gh.create_issue`, `settings.get`, `self.held`, `self.session`, `issue_text`, `assignment`, `gh.close`, `self.hold_start_error`, `self.fail_or_retry`, `i.get`, `gh.linked_prs`, `report_facts`, `p.get`, `gh.is_agent_pr`, `gh.file`, `get`, `gh.comment`; stamp `<!-- code: 73a196189485 -->`: branch lines not in its Branches and errors table: 738, 741, 744, 748, 749, 751, 753, 756, 759, 762, 764, 765
  - card `Queue.render` (method, lines 778-788) - branch lines to cite: 785, 787; calls: `rows.items`, `().isoformat`, `json.dumps`, `now`, `join`, `self.gh.set_body`, `body.split`, `split`, `tracker.get`, `self.log`; stamp `<!-- code: 651906b39ffd -->`: branch lines not in its Branches and errors table: 785, 787
  - card `Queue.delta` (method, lines 791-817) - branch lines to cite: 795, 803, 805; calls: `gh.default_branch`, `json_file`, `self.log`, `gh.file`, `sys.path.insert`, `os.path.abspath`, `os.path.join`, `components.rows_of`, `sorted`, `().values`, `components.component_map`, `p.startswith`, `gh.issues`, `gh.create_issue`, `assignment`, `comp_label`, `join`, `len`, `components.assign`; stamp `<!-- code: 173a0090e878 -->`: branch lines not in its Branches and errors table: 795, 803, 805
  - card `main` (function, lines 820-863) - branch lines to cite: 837, 838, 842, 843, 844, 846, 847, 849, 850, 856, 862, 863; calls: `argparse.ArgumentParser`, `__doc__.splitlines`, `parser.add_subparsers`, `sub.add_parser`, `start.add_argument`, `d.add_argument`, `parser.parse_args`, `os.environ.get`, `SystemExit`, `GitHub`, `Queue`, `gh.ensure_labels`, `gh.issues`, `gh.create_issue`, `print`, `n.strip`, `any`, `queue.reconcile`, `queue.delta`, `str` and 7 more (ledger/symbol-checklist.md); stamp `<!-- code: f407f91f47e7 -->`: branch lines not in its Branches and errors table: 838, 842, 846, 847, 849, 850, 856, 862, 863

When every item is written, tick the packet in progress.md, write one line to the user, and run next.py again.
Keep going: run next.py after every packet until it prints NEW CHAT or DONE. Do not end your turn in between.
Command: python3 -I .github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep
```
