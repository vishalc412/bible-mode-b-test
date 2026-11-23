---
id: lld/tools/fanout
kind: module
component: tools
source: tools/fanout.sh
summary: Creates labeled GitHub issues for planned components
reads: [file:codebase-analysis/plan.json]
writes: []
calls: [external:GitHub CLI]
uses: [symbol:Bash, symbol:python3, symbol:gh]
config: [config:ENGINE]
exposes: []
publishes: []
consumes: []
---

# fanout

Source file: `tools/fanout.sh`

| | |
| --- | --- |
| Component | `tools` (its design page is `README.md` in this folder) |
| Lines | 31 |
| Role | Creates GitHub labels and one component-analysis issue per component in `plan.json`, using the selected issue-assignment mode. |
| Imports that matter | Bash built-ins, `python3` with the standard-library `json` module, and the `gh` command (`tools/fanout.sh:1`, `tools/fanout.sh:9-12`, `tools/fanout.sh:25-29`) |
| Module-level state | Enables `-euo pipefail`; sets `repo` from `$1`, `engine` from `ENGINE` or `copilot`, and populates `components` from the JSON plan (`tools/fanout.sh:6-9`). |

## Summary

`fanout.sh` reads component names from `codebase-analysis/plan.json`, creates a shared `agent:claude` label, then creates a `component:<name>` label and issue for each component. The issue's assignee and body depend on `ENGINE`: the default `copilot` mode assigns `@copilot`; `claude` mode rewrites `@copilot` in the body and applies the `agent:claude` label (`tools/fanout.sh:7-30`).

## Index

| Symbol | Kind | Lines | Card |
| --- | --- | --- | --- |
| Script entry point | Bash script | 1-31 | [script flow](#module-level-code) |

## Call graph

No functions are declared in this file. The entry-point script calls `python3` to read the plan and uses `gh` commands to create labels and issues (`tools/fanout.sh:9-12`, `tools/fanout.sh:25-29`).

## Classes

None.

## Functions and methods

None.

## Module-level code

1. Sets Bash options `-euo pipefail`, takes the repository identifier from `$1`, and sets `engine` from `ENGINE` or defaults it to `copilot` (`tools/fanout.sh:6-8`).
2. Uses `python3 -c` to open `codebase-analysis/plan.json`, read its `components` keys, join them with spaces, and assign that output to `components` (`tools/fanout.sh:9`).
3. Creates or forces the `agent:claude` label in the selected repository, using color `7057ff`, and redirects the command's standard output to `/dev/null` (`tools/fanout.sh:10`).
4. Iterates over words in `components`. For each `c`, creates or forces the `component:$c` label with color `1d76db`, then builds an issue body with the component name, pass-1 scope and gate command, and directions for later passes (`tools/fanout.sh:11-23`).
5. In `case "$engine"`, `copilot` creates an issue titled `Analyze component: $c`, with the body and `component:$c` label, assigned to `@copilot`; `claude` creates the same title, replaces `@copilot` with `@claude` in the body, and adds both `component:$c` and `agent:claude` labels. Other values print `unknown ENGINE <value>` to standard error and exit with status `2` (`tools/fanout.sh:24-30`).
6. Continues the loop for remaining components (`tools/fanout.sh:11`, `tools/fanout.sh:31`).

**Pseudo-code**

```text
enable Bash error, unset-variable, and pipeline checks
repo = first argument
engine = ENGINE if set and nonempty, otherwise "copilot"
components = space-joined component keys from codebase-analysis/plan.json
create agent:claude label in repo
for each component:
    create component label
    build the component analysis issue body
    if engine is copilot: create issue assigned to @copilot
    else if engine is claude: replace @copilot with @claude and create labeled issue
    otherwise: print error and exit 2
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `tools/fanout.sh:8` | default-value expansion | `ENGINE` is unset or empty | Sets `engine` to `copilot`; otherwise uses `ENGINE` (`tools/fanout.sh:8`). |
| `tools/fanout.sh:11` | `for` | For each word in the unquoted `components` expansion | Creates a component label and issue according to `engine` (`tools/fanout.sh:11-30`). |
| `tools/fanout.sh:24` | `case` | `engine` equals `copilot` | Runs `gh issue create` with `--assignee "@copilot"` and the component label (`tools/fanout.sh:25-26`). |
| `tools/fanout.sh:24` | `case` | `engine` equals `claude` | Replaces `@copilot` with `@claude` in the body and creates the issue with component and agent labels (`tools/fanout.sh:27-28`). |
| `tools/fanout.sh:24` | default case | `engine` is neither `copilot` nor `claude` | Prints the unknown-engine message to standard error and exits `2` (`tools/fanout.sh:29`). |

**Output and side effects**: Invokes GitHub CLI commands targeting the supplied repository to create labels and component issues; the `agent:claude` label command's standard output is discarded (`tools/fanout.sh:10-12`, `tools/fanout.sh:25-29`). When there are no component keys, it still attempts the shared label creation and the loop body runs zero times (`tools/fanout.sh:9-11`).

## Surprises

The generated issue body directs the recipient to `.github/skills/component-analysis/SKILL.md` (`tools/fanout.sh:13-15`), but the repository skill inventory has no `component-analysis/SKILL.md` (inferred: listing `.github/skills/**/SKILL.md` returned only the seven named skills and none under `component-analysis/`). The available analysis skill is `.github/skills/analyzing-a-codebase/SKILL.md` (`.github/skills/analyzing-a-codebase/SKILL.md:1-3`). It is unclear whether the prompt names an intentionally external skill or an outdated path; see Q1 in `ledger/components/tools/questions.md`.
