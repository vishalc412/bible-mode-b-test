Title: Codebase analysis - component tools

Use the analyzing-a-codebase skill (in .github/skills) in component mode for `tools` only.
Size: 3 source files, 3 packets, about 2 sessions. Calls into: none. Called by: none.

Start every session with:
  python3 -I .github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --component tools --new-session
and do exactly what it prints, running it again after each job, until it tells you to stop.

Write only inside these folders (other components work in parallel on other pull requests):
  codebase-analysis/lld/tools/
  codebase-analysis/lld/api/tools/
  codebase-analysis/ledger/components/tools/

Stop and end the session when next.py prints NEW CHAT, COMPONENT DONE, WAITING FOR ANSWERS,
STOP or DONE. Before you stop, write in the pull request description:
  - what you finished in this session,
  - the first line next.py printed last (for example "NEW CHAT" or "COMPONENT DONE tools"),
  - any questions for the person, numbered.
If you hit a question only a person can answer, add it to codebase-analysis/ledger/components/tools/questions.md as a line "- [ ] Q1. ...",
then run next.py: it prints WAITING FOR ANSWERS and you stop.
When this pull request already has answers from the person, write each under its question,
change "- [ ]" to "- [x]", then run next.py again.
A failed call is a stop, not a restart: if a command or model request fails twice, stop and say what failed.

When it prints COMPONENT DONE, the next step is a verification of this component in a new session
on a different model (the person asks for it with an @copilot comment on this pull request).
