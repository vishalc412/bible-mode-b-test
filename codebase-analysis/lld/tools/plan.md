---
id: lld/tools/plan
kind: module
component: tools
source: tools/plan.py
summary: Scans component Python files and writes the analysis plan
reads: [file:components/*/*.py]
writes: [file:codebase-analysis/plan.json]
calls: []
uses: [symbol:count_tests]
config: []
exposes: []
publishes: []
consumes: []
---

# plan

Source file: `tools/plan.py`

| | |
| --- | --- |
| Component | `tools` (its design page is `README.md` in this folder) |
| Lines | 62 |
| Role | Inventories each non-private component directory's Python files, functions, test functions, and literal HTTP URLs, then writes `codebase-analysis/plan.json`. |
| Imports that matter | Python `ast`, `json`, `pathlib`, `re`, and `sys`; `count_tests` imported from the sibling `gate` module (`tools/plan.py:8-15`) |
| Module-level state | Adds the resolved `tools` directory to `sys.path`, defines repository `ROOT`, and compiles `HTTP` to match quoted `http://` literals (`tools/plan.py:14-18`). |

## Summary

`plan.py` builds the deterministic input used by the component analysis gate. `main` visits directories below `components`, skipping non-directories and names beginning with `_`; `scan` classifies each Python file, inventories function definitions and matching HTTP literals in non-test files, and counts test functions via `gate.count_tests`. The resulting versioned plan includes descriptions for passes 1-3 and is serialized to `codebase-analysis/plan.json` (`tools/plan.py:21-38`, `tools/plan.py:41-58`).

## Index

| Symbol | Kind | Lines | Card |
| --- | --- | --- | --- |
| `scan` | function | 21-38 | [card](#scancomponent_dir) |
| `main` | function | 41-58 | [card](#main) |

## Call graph

```mermaid
flowchart LR
  main["main"]
  scan["scan"]
  gatecounttests["gate.count_tests"]
  main -->|"inventory each component"| scan
  scan -->|"count test functions"| gatecounttests
```

## Classes

None.

## Functions and methods

### `scan(component_dir)`

Source: `tools/plan.py:21-38` <!-- code: 86c2bf11760e -->

| | |
| --- | --- |
| Kind | function |
| Called by | `main` (`tools/plan.py:45`) |
| Calls | `sorted`, `component_dir.glob`, `Path.relative_to`, `Path.as_posix`, `path.name.startswith`, `Path.read_text`, `ast.walk`, `ast.parse`, `isinstance`, `enumerate`, `text.splitlines`, `HTTP.finditer`, `match.group`, `functions.append`, `http_sites.append`, `gate.count_tests` |
| Purpose | Returns a component's source-file, test-file, function, test-count, and HTTP-literal inventory. |

**Inputs**

| Name | Type | Meaning | Checked how |
| --- | --- | --- | --- |
| `component_dir` | `pathlib.Path` | Directory containing one component's Python files | Globbed for immediate `*.py` children; no explicit validation (`tools/plan.py:23`) |

**Steps**

1. Initializes empty `sources`, `tests`, `functions`, and `http_sites` lists (`tools/plan.py:22`).
2. Iterates over sorted immediate `*.py` paths; skips `__init__.py` (`tools/plan.py:23-25`).
3. Converts each remaining path to a repository-relative POSIX path and appends it to `tests` when its basename starts with `test_`, otherwise to `sources` (`tools/plan.py:26-27`).
4. Reads every remaining file. For non-test files, parses its Python AST and records every `ast.FunctionDef` as its function name and `<relative path>:<line>` (`tools/plan.py:28-32`).
5. For each non-test file line, finds matches of the compiled quoted-`http://` pattern and records the matched URL and `<relative path>:<line>` (`tools/plan.py:33-35`; pattern: `tools/plan.py:18`).
6. Counts test functions in the `tests` paths using `gate.count_tests` and returns all five inventory fields (`tools/plan.py:36-38`).

**Pseudo-code**

```text
initialize file, function, and HTTP-site lists
for each sorted immediate *.py file:
    skip __init__.py
    store its repository-relative POSIX path as test or source
    read its text
    if it is not a test:
        parse AST and record each function definition with its line
        find quoted http:// literals per line and record URL plus line
count test functions in the test paths via gate.count_tests
return sources, tests, test_count, functions, and http_sites
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `tools/plan.py:23` | `for` | For each sorted immediate `*.py` child | Processes that path (`tools/plan.py:23-36`). |
| `tools/plan.py:24` | `if` | The basename is `__init__.py` | Skips the file; otherwise continues inventory (`tools/plan.py:24-25`). |
| `tools/plan.py:27` | conditional expression | The basename starts with `test_` | Appends to `tests`; otherwise appends to `sources` (`tools/plan.py:27`). |
| `tools/plan.py:29` | `if` | The basename does not start with `test_` | Parses and scans the file for functions and HTTP literals; test files are omitted from those inventories (`tools/plan.py:29-35`). |
| `tools/plan.py:30` | `for` | For each AST node returned by `ast.walk` | Checks whether it is a function definition (`tools/plan.py:30-32`). |
| `tools/plan.py:31` | `if` | The AST node is an `ast.FunctionDef` | Appends its name and source location (`tools/plan.py:31-32`). |
| `tools/plan.py:33` | `for` | For each line of a non-test file | Searches that line for the HTTP pattern (`tools/plan.py:33-35`). |
| `tools/plan.py:34` | `for` | For each match found in the line | Appends its URL and source location (`tools/plan.py:34-35`). |

**Output and side effects**: Returns a dictionary with `sources`, `tests`, `test_count`, `functions`, and `http_sites`; reads component files and delegates test counting to `gate.count_tests` (`tools/plan.py:28-38`). Nothing in `scan` catches an error: a file that cannot be read or a syntax error in a source or test file raises to `main`, which has no handler either, so the run ends without writing `plan.json` (assumed: library behaviour of `read_text` and `ast.parse`) (`tools/plan.py:28`, `tools/plan.py:30`, `tools/plan.py:36`, `tools/plan.py:45`; `tools/gate.py:36`).

### `main()`

Source: `tools/plan.py:41-58` <!-- code: fec6042cdffb -->

| | |
| --- | --- |
| Kind | function |
| Called by | Python module entry point (`tools/plan.py:61-62`) |
| Calls | `sorted`, `Path.iterdir`, `Path.is_dir`, `str.startswith`, `scan`, `Path.mkdir`, `json.dumps`, `Path.write_text`, `print`, `Path.relative_to`, `len` |
| Purpose | Scans component directories and writes a JSON plan with component inventories and pass descriptions. |

**Steps**

1. Initializes an empty `components` mapping and iterates through sorted children of `ROOT / "components"` (`tools/plan.py:42-43`).
2. For each directory whose name does not start with `_`, assigns `scan(d)` to `components[d.name]` (`tools/plan.py:44-45`).
3. Builds the plan object with version `1`, three named pass descriptions, and the component mapping (`tools/plan.py:46-54`).
4. Sets the output path to `ROOT / "codebase-analysis" / "plan.json"`, creates its parent directory with `exist_ok=True`, and writes indented JSON followed by a newline (`tools/plan.py:55-57`).
5. Prints the repository-relative output path and number of components (`tools/plan.py:58`).

**Pseudo-code**

```text
components = {}
for each sorted entry in ROOT/components:
    if it is a directory and its name does not start with "_":
        components[name] = scan(directory)
plan = version 1, pass descriptions 1-3, and components
create plan.json parent directory if it does not exist
write indented JSON plus a newline
print relative output path and component count
```

**Branches and errors**

| Line | Branch | When | What happens |
| --- | --- | --- | --- |
| `tools/plan.py:43` | `for` | For each sorted entry in `ROOT / "components"` | Evaluates whether to include the entry (`tools/plan.py:43-45`). |
| `tools/plan.py:44` | `if` | The entry is a directory and its name does not begin with `_` | Scans and stores it; otherwise skips it (`tools/plan.py:44-45`). |

**Output and side effects**: Writes `codebase-analysis/plan.json` as formatted JSON with a trailing newline and prints its relative path and component count (`tools/plan.py:55-58`).

**Errors**: `main` has no handler. A missing `components/` directory makes `iterdir` raise at line 43, and a file that cannot be read or has a syntax error makes `scan` raise at line 45 (`scan` catches nothing; assumed: library behaviour of `Path.iterdir`, `Path.read_text` and `ast.parse`); in both cases the exception ends the run before the write at lines 55-57, so `plan.json` is not written again (`tools/plan.py:43-45`, `tools/plan.py:55-57`).

## Module-level code

The module inserts the resolved `tools` directory at the front of `sys.path` (`sys.path.insert(0, ...)`) before importing `count_tests` from `gate`; it computes `ROOT` from the parent of that directory and compiles the HTTP-literal regular expression at import time (`tools/plan.py:14-18`). When run directly, it calls `main()` (`tools/plan.py:61-62`).

## Surprises

None identified in this file.

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
