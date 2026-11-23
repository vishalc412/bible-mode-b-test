Title: Codebase analysis - assemble the whole bible

Every component pull request is merged. Use the analyzing-a-codebase skill (in .github/skills) without --component:
  python3 -I .github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --depth deep --new-session
It hands out the whole-system passes: sweep, data dictionary, HLD, mind map, front page, reference,
knowledge base and the full quality gate, which also checks that each component's page names its callers.
Continue until it prints DONE, then record the baseline as it says (delta.py --init).

Stop and end the session when next.py prints NEW CHAT, COMPONENT DONE, WAITING FOR ANSWERS,
STOP or DONE. Before you stop, write in the pull request description:
  - what you finished in this session,
  - the first line next.py printed last (for example "NEW CHAT" or "COMPONENT DONE "),
  - any questions for the person, numbered.
If you hit a question only a person can answer, add it to codebase-analysis/ledger/questions.md as a line "- [ ] Q1. ...",
then run next.py: it prints WAITING FOR ANSWERS and you stop.
When this pull request already has answers from the person, write each under its question,
change "- [ ]" to "- [x]", then run next.py again.
A failed call is a stop, not a restart: if a command or model request fails twice, stop and say what failed.

After DONE, the person asks for a verification of the whole analysis in a new session on a different model
