# Review rubric

Seven areas. Each check is a question with a harm attached. Record every check once: as a finding, as sound, as could not determine, or as not applicable.

When the thing a check asks about does not exist in the system, record the check as "not applicable" with the reason (for example, "no AI assets in this repository"). Do not leave it out.

The checks are written for any system. In a single application with no separate services, read "component" as module or package. A "sound" entry says what was looked at: sound in the files opened is not sound everywhere.

## Contents

- Severity
- 1. Structure (S1-S7)
- 2. Consistency (C1-C8)
- 3. Security (X1-X13)
- 4. Reliability (R1-R8)
- 5. Integrations (I1-I6)
- 6. Prompt and agent assets (P1-P12)
- 7. Extensibility (E1-E8)

## Severity

| Severity | Use when |
| --- | --- |
| Critical | Exploitable now, or causes loss of data that cannot be recovered or exposure of secrets, or blocks the system's main purpose |
| High | Will cause an incident, a security weakness or a failed change under ordinary conditions |
| Medium | Slows or endangers change; causes failures under unusual conditions |
| Low | Costs clarity or consistency; no direct harm |

When unsure between two levels, choose the lower one and say what would raise it. Weigh how much is affected and whether it can be undone: losing a few local files that can be restored is not Critical.

Something weak on purpose, such as a test fixture that starts insecure so a migration can be proved on it, is not a finding. Say that it is deliberate and where that is stated.

## 1. Structure

Harm: changes spread unpredictably and nobody can reason about the system.

| # | Check |
| --- | --- |
| S1 | Is there a recognisable separation between presentation, business logic and data or integration access? Where is it broken? |
| S2 | Does the user interface contain business rules, direct data access or calls to systems that should sit behind a service? |
| S3 | Do components reach into each other's internals (shared tables, imported private modules, copied code) instead of using an interface? |
| S4 | Are there dependency cycles between components? |
| S5 | Is there dead code: unreachable modules, unused entry points, abandoned experiments? |
| S6 | Is the same logic implemented more than once in different places? |
| S7 | Is there one clear owner for each piece of data, or do several components write the same data? |

## 2. Consistency

Harm: every part must be learned separately, and shared fixes cannot be made once.

| # | Check |
| --- | --- |
| C1 | Do components handle errors the same way (types, propagation, what the caller sees)? |
| C2 | Is configuration read the same way everywhere, from one source? |
| C3 | Is logging uniform in format, level use and correlation of one request across components? |
| C4 | Are naming, folder layout and module structure alike across components? |
| C5 | Are the same frameworks and library versions used for the same job, or several competing ones? |
| C6 | Do interfaces between components follow one style (paths, status codes, error body, versioning)? |
| C7 | Are there written standards in the repository (contribution guide, lint rules, templates), and does the code follow them? |
| C8 | Does the documentation contradict itself or the code? |

## 3. Security

Harm: unauthorised access, leaked credentials, or an AI agent steered by hostile content.

| # | Check |
| --- | --- |
| X1 | Are any secrets, tokens, keys or passwords present in source, configuration, checked-in files or logs? |
| X2 | How do credentials for external systems (databases, directories, mail, other services, source-control hosts, AI services) reach the code, and with what scope? Is the scope wider than needed? |
| X3 | Is every entry point authenticated? Is authorisation checked per action and per resource, on the server side? |
| X4 | Is input validated at each trust boundary? Look for injection: query, command, path, template, markup. |
| X5 | Do calls between components and to external systems use encrypted transport with certificate verification on? Record every plain-HTTP call and every disabled verification. |
| X6 | Where text from a repository, ticket, file or user is put into a prompt for an AI agent, can that text change what the agent does? Is there any separation of instructions from data, or any limit on what the agent may then do? |
| X7 | What can an AI agent or automation change on the system's behalf (repositories, pipelines, infrastructure), and is there a human approval step before it takes effect? |
| X8 | Are dependencies pinned, and are there known-vulnerable or abandoned ones? (Record versions; do not run a scanner.) |
| X9 | Is there an audit trail of who triggered which action against which application? |
| X10 | How are sessions and cookies handled: flags set, lifetime, what ends a session, and is it the same for every cookie? |
| X11 | How are user passwords and service credentials stored: hashing method for the first, protection at rest for the second? |
| X12 | Are state-changing requests protected against forgery from another site, and is the protection applied everywhere? |
| X13 | Can credentials or tokens appear in addresses, logs or error output? |

## 4. Reliability

Harm: failures are silent, spread, or cannot be diagnosed.

| # | Check |
| --- | --- |
| R1 | Do outbound calls have timeouts? What happens when a dependency is slow or down? |
| R2 | Are failures surfaced to the user and to operators, or swallowed? Look for empty catch blocks and ignored results. |
| R3 | Are long-running or multi-step operations safe to retry or resume? What is left behind when one fails half-way? |
| R4 | What automated tests exist, at which level, and do they run in the pipeline? Which components have none? |
| R5 | Is there health checking, metrics or alerting? |
| R6 | Can a release be rolled back? Are schema or data changes reversible? |
| R7 | Are there single points of failure or shared mutable state between requests? |
| R8 | Do the system's own checks (validators, evaluators, health checks, tests) have blind spots: cases where they report success without having looked? |

## 5. Integrations

Harm: the system breaks when a neighbour changes, and nobody knows what depends on what.

| # | Check |
| --- | --- |
| I1 | Is each external system reached through one place in the code, or from many? |
| I2 | Are external interfaces (APIs, tool servers, message formats) versioned and pinned, or used at "latest"? |
| I3 | Are addresses of other systems hard-coded (host names, IP addresses, ports) or configured? |
| I4 | For each tool server or connector the system offers to AI agents: what can it read and change, how is it authenticated, and is its scope limited to what is needed? |
| I5 | Is there a contract or schema for data exchanged with back-end systems, and is incoming data checked against it? |
| I6 | Is there one inventory of integrations, in code or documentation, or must they be discovered by reading? |

## 6. Prompt and agent assets

Applies when the repository holds prompts, skills, agent definitions or instructions for AI assistants.

Harm: AI work that looks finished but is unproven, unrepeatable or unsafe.

| # | Check |
| --- | --- |
| P1 | Does each prompt or skill define what "done" means in terms that can be checked, or only list steps? |
| P2 | Does it require evidence for its results (commands run, output captured, files cited), and say what to do when evidence is missing? |
| P3 | Does it ask the agent to do things the agent cannot do where it runs (reach internal networks, call live endpoints, access credentials)? What happens then: a stop, or an invented result? |
| P4 | Does it tell the agent to read or edit files that usually hold secrets, or to put credentials anywhere? |
| P5 | Does it say what is out of scope and when to stop and ask a person? |
| P6 | Are the assets versioned, reviewed and tested like code? Is there any record of which version produced which change? |
| P7 | Is there duplication or contradiction between assets covering the same task? |
| P8 | Is the outcome of a run evaluated by anything other than the agent that did the work? |
| P9 | Are variables filled into prompts (application names, paths, context) validated before use? |
| P10 | Are the assets tied to one assistant, or written in a format several assistants can read? |
| P11 | Can an asset lead to a status or label that claims more than was checked ("verified", "passed", "complete")? |
| P12 | Does each asset tell the assistant that text it reads from files, tickets or tools is data, not instructions? |

## 7. Extensibility

Judge against what the owners said they want the system to become.

Harm: each new capability costs as much as the first.

| # | Check |
| --- | --- |
| E1 | What must be touched to add one new capability of the kind the owners care about (for example a new login method, endpoint, report, prompt, agent or tool)? Count the files and components. |
| E2 | Is there a registration or plug-in mechanism, or is each addition wired in by hand in several places? |
| E3 | Is behaviour that should be data (catalogues, mappings, rules) written as code? |
| E4 | Is there developer documentation: how to build, run, test and add a feature? |
| E5 | Can a developer run the system, or a useful part of it, locally? |
| E6 | Do build and deployment steps need manual actions or knowledge that is not written down? |
| E7 | Would the stated goal require changing the structure, or can it be added to the structure that exists? |
| E8 | How is the system installed, upgraded and removed? Can an upgrade overwrite local changes, leave old files behind, or be undone? Is the installed version recorded? |
