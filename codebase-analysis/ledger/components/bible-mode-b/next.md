```text
NEXT PACKET 1 of 4 (0 done, 0%; 0 in this chat, budget 6)
Component: bible-mode-b
Read:      .github/bible/bible_queue.py lines 1-306 (of 844), in full
Write:     codebase-analysis/lld/bible-mode-b/bible_queue.md (create; right under its title: Source file: `.github/bible/bible_queue.py`)
Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card

To do in this packet (37):
  - no page declares this file
  - card `GitHub` (class, lines 88-302) - branch lines to cite: none; calls: none; stamp `<!-- code: fa8466d1289a -->`: not named on the page
  - card `GitHub.__init__` (method, lines 89-92) - branch lines to cite: none; calls: `rstrip`, `os.environ.get`; stamp `<!-- code: b511658beb68 -->`: not named on the page
  - card `GitHub.request` (method, lines 94-103) - branch lines to cite: 95, 99, 101; calls: `().encode`, `json.dumps`, `urllib.request.Request`, `req.add_header`, `urllib.request.urlopen`; stamp `<!-- code: 1f8902892005 -->`: not named on the page
  - card `GitHub.call` (method, lines 105-117) - branch lines to cite: 106, 110, 111, 114, 115, 116, 117; calls: `path.startswith`, `self.request`, `resp.read`, `RuntimeError`, `().decode`, `err.read`, `path.split`, `json.loads`; stamp `<!-- code: 753c5f1a3922 -->`: not named on the page
  - card `GitHub.paged` (method, lines 119-127) - branch lines to cite: 121, 122, 125; calls: `self.call`, `len`; stamp `<!-- code: 1bb6c1899527 -->`: not named on the page
  - card `GitHub.issues` (method, lines 129-131) - branch lines to cite: none; calls: `urllib.parse.quote`, `join`, `self.paged`; stamp `<!-- code: b3f969457f25 -->`: not named on the page
  - card `GitHub.ensure_label` (method, lines 133-138) - branch lines to cite: 134, 136; calls: `self.paged`, `self.call`, `self.known_labels.add`; stamp `<!-- code: c80387a5616e -->`: not named on the page
  - card `GitHub.ensure_labels` (method, lines 140-142) - branch lines to cite: 141; calls: `LABELS.items`, `self.ensure_label`; stamp `<!-- code: 3233fadcc4c0 -->`: not named on the page
  - card `GitHub.create_issue` (method, lines 144-151) - branch lines to cite: 145, 148; calls: `self.ensure_label`, `LABELS.get`, `self.call`; stamp `<!-- code: c0db4afc186c -->`: not named on the page
  - card `GitHub.default_branch` (method, lines 153-154) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: 4eb167486c4d -->`: not named on the page
  - card `GitHub.branch_sha` (method, lines 156-158) - branch lines to cite: 158; calls: `self.call`, `urllib.parse.quote`; stamp `<!-- code: 446defb234bd -->`: not named on the page
  - card `GitHub.create_branch` (method, lines 160-161) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: b860758c1ca1 -->`: not named on the page
  - card `GitHub.reset_branch` (method, lines 163-164) - branch lines to cite: none; calls: `self.call`, `urllib.parse.quote`; stamp `<!-- code: 43e383793681 -->`: not named on the page
  - card `GitHub.file` (method, lines 166-170) - branch lines to cite: 168; calls: `self.call`, `urllib.parse.quote`, `isinstance`, `().decode`, `base64.b64decode`; stamp `<!-- code: e383f7bd9e38 -->`: not named on the page
  - card `GitHub.prs` (method, lines 172-174) - branch lines to cite: 173; calls: `urllib.parse.quote`, `self.paged`; stamp `<!-- code: e46dcb273277 -->`: not named on the page
  - card `GitHub.timeline` (method, lines 176-177) - branch lines to cite: none; calls: `self.paged`; stamp `<!-- code: 6df4539072ff -->`: not named on the page
  - card `GitHub.linked_prs` (method, lines 179-188) - branch lines to cite: 182, 185; calls: `self.timeline`, `get`, `source.get`, `nums.append`, `event.get`, `self.call`, `sorted`, `set`; stamp `<!-- code: 91e30cd14abd -->`: not named on the page
  - card `GitHub.branch_prs` (method, lines 190-193) - branch lines to cite: none; calls: `self.repo.split`, `self.paged`, `urllib.parse.quote`; stamp `<!-- code: fa42118d7d5a -->`: not named on the page
  - card `GitHub.agent_events` (method, lines 195-199) - branch lines to cite: none; calls: `e.get`, `self.timeline`, `get`; stamp `<!-- code: 23a18c0ca1f4 -->`: not named on the page
  - card `GitHub.is_agent_pr` (method, lines 201-205) - branch lines to cite: 203; calls: `get`, `pr.get`, `any`, `self.agent_events`; stamp `<!-- code: 5e675426c513 -->`: not named on the page
  - card `GitHub.start_error` (method, lines 207-215) - branch lines to cite: 210, 212; calls: `self.assigned_at`, `self.timeline`, `get`, `START_ERROR.search`, `e.get`, `().splitlines`, `strip`; stamp `<!-- code: d25f1505b57a -->`: not named on the page
  - card `GitHub.assigned_at` (method, lines 217-220) - branch lines to cite: 220; calls: `e.get`, `self.timeline`, `max`; stamp `<!-- code: 8dec0d30b502 -->`: not named on the page
  - card `GitHub.pr_files` (method, lines 222-229) - branch lines to cite: 225, 227; calls: `self.paged`, `out.append`, `f.get`; stamp `<!-- code: 4c64f0e6b538 -->`: not named on the page
  - card `GitHub.commit_time` (method, lines 231-232) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: a3036655ce65 -->`: not named on the page
  - card `GitHub.tarball` (method, lines 234-259) - branch lines to cite: 242, 243, 247, 249, 252, 254; calls: `urllib.parse.quote`, `tempfile.TemporaryFile`, `buf.seek`, `os.path.abspath`, `tarfile.open`, `self.request`, `shutil.copyfileobj`, `RuntimeError`, `member.name.split`, `os.path.normpath`, `member.isdir`, `os.makedirs`, `os.path.join`, `target.startswith`, `os.path.dirname`, `tar.extractfile`, `open`, `len`, `member.isfile`; stamp `<!-- code: 37cdbd678a08 -->`: not named on the page
  - card `GitHub.label` (method, lines 261-263) - branch lines to cite: none; calls: `self.ensure_label`, `LABELS.get`, `self.call`; stamp `<!-- code: 3c67a9360e66 -->`: not named on the page
  - card `GitHub.unlabel` (method, lines 265-266) - branch lines to cite: none; calls: `self.call`, `urllib.parse.quote`; stamp `<!-- code: caf34958b931 -->`: not named on the page
  - card `GitHub.comment` (method, lines 268-269) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: a05e7f494734 -->`: not named on the page
  - card `GitHub.close` (method, lines 271-272) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: db2a40d380a0 -->`: not named on the page
  - card `GitHub.set_body` (method, lines 274-275) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: 56545a0f998b -->`: not named on the page
  - card `GitHub.unassign` (method, lines 277-278) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: 415484346894 -->`: not named on the page
  - card `GitHub.assign` (method, lines 280-281) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: 8fb2f09224db -->`: not named on the page
  - card `GitHub.ready` (method, lines 283-291) - branch lines to cite: 286, 290, 291; calls: `self.api.endswith`, `len`, `self.request`, `resp.read`, `RuntimeError`; stamp `<!-- code: ae31dacf00e7 -->`: not named on the page
  - card `GitHub.merge` (method, lines 293-296) - branch lines to cite: 294; calls: `pr.get`, `self.ready`, `self.call`; stamp `<!-- code: 68adaed91bed -->`: not named on the page
  - card `GitHub.close_pr` (method, lines 298-299) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: c5e4b3b311ae -->`: not named on the page
  - card `GitHub.create_pr` (method, lines 301-302) - branch lines to cite: none; calls: `self.call`; stamp `<!-- code: 9b2aa4667c1c -->`: not named on the page

When every item is written, write one line to the user, and run next.py again.
Write only under lld/bible-mode-b/, lld/api/bible-mode-b/ and ledger/components/bible-mode-b/: other components run in parallel.
Keep going: run next.py after every packet until it prints NEW CHAT or COMPONENT DONE. Do not end your turn in between.
Command: python3 -I /home/runner/work/bible-mode-b-test/bible-mode-b-test/.github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component bible-mode-b
```
