Title: Codebase analysis - plan the components

Use the analyzing-a-codebase skill (in .github/skills) for passes 1 and 2 only:
  python3 -I .github/skills/analyzing-a-codebase/scripts/next.py --repo . --analysis codebase-analysis --new-session
Follow what it prints for pass 1 (inventory) and pass 2 (write the `## Components` table in codebase-analysis/progress.md).
Then run:
  python3 -I .github/skills/analyzing-a-codebase/scripts/discover.py --repo . --analysis codebase-analysis
and fix the plan until it exits 0. It writes components.json, components.md and the issue texts.
Do not start on any component. Show the table from components.md to the person in the pull request description:
they choose the components there (when it says to ask the user which components, this is how).
Do not edit anything outside codebase-analysis/.
