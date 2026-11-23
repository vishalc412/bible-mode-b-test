# Progress

Repository: `/home/runner/work/bible-mode-b-test/bible-mode-b-test`
Depth: deep
Started: 2026-11-23
Version: not provided

## Pass 1 — Inventory

- Inventory snapshot: 20 in-scope files, 14 source files, 1,320 source lines, 108 classes and functions, 0 routes.
- The generated file list and symbol checklist are in `ledger/inventory.json` and `ledger/symbol-checklist.md`.
- The coverage ledger is `ledger/coverage-ledger.md`; all 20 files are not yet read.
- Excluded: `.git`, `codebase-analysis`, and the repository's `.github/skills/*` toolkits, as listed in the inventory checklist.

## Work plan

| Pass | Work | Status |
| --- | --- | --- |
| 1 | Inventory and coverage ledger | done |
| 2 | Components and packet plan; run discovery | done |
| 3–5 | Component LLD pages and design pages | done |
| 6 | Search sweep | done |
| 7 | Whole-system data dictionary | done |
| 8 | HLD pages | in progress |
| 9–11 | Mind map/front page/reference, knowledge base, quality gate | pending |

## Components

| Component | Folders and files | Language | Starts by | Entry points | Packets |
| --- | --- | --- | --- | --- | ---: |
| `catalog` | `components/catalog/` | Python 3; standard-library HTTP server (`components/catalog/service.py:7-12`) | `python3 -m components.catalog.service` (`components/catalog/service.py:40-48`) | `CatalogHandler.do_GET`, `make_server` (`components/catalog/service.py:24-43`) | 3 |
| `orders` | `components/orders/` | Python 3; standard library (`components/orders/orders.py:1-5`) | Imported and called by Python code (`components/orders/test_orders.py:1-8`) | `line_total`, `order_total`, `validate`, `settle` (`components/orders/orders.py:19-51`) | 4 |
| `bible-mode-b` | `.github/bible/`, `.github/workflows/` | Python 3 and GitHub Actions YAML (`.github/bible/bible_queue.py:1-10`) | Manual dispatch, 15-minute schedule, and default-branch push workflows (`.github/workflows/bible-plan.yml:7-8`, `.github/workflows/bible-queue.yml:7-10`, `.github/workflows/bible-delta.yml:6-10,16-18`, `.github/workflows/poc-assign-copilot.yml:11-13`) | `bible_queue.py start`, `reconcile`, `delta` (`.github/bible/bible_queue.py:1-10,797-844`) | 4 |
| `tools` | `tools/` | Python 3 and Bash (`tools/plan.py:8-15`, `tools/fanout.sh:1-6`) | CLI and shell invocation (`tools/plan.py:41-61`, `tools/gate.py:81-116`, `tools/fanout.sh:1-6`) | `plan.py`, `gate.py`, `fanout.sh` (`tools/plan.py:41-61`, `tools/gate.py:81-116`, `tools/fanout.sh:1-6`) | 3 |

Discovery succeeded and wrote `components.json`, `components.md`, and issue texts under `ledger/issues/`. The component analyses were completed in separate pull requests. The whole-system pass is now being assembled.

At this session's start, `next.py` reported 11 of 13 packets done. Packet 2 refreshed the `bible-mode-b` cards for lines 307–662; packet 3 refreshed the cards for lines 663–867.

## Sweep

- Searched in-scope source and documentation with `rg --hidden`; excluded `.git`, `codebase-analysis`, and `.github/skills` using `**`-scoped globs. Verified the excluded trees did not appear in the file list.
- Counts below are matching lines for the listed literal regular expressions. Categories overlap and are conservative search leads, not counts of confirmed runtime behaviors.

| Surface | File types | Search patterns | Matching lines | Disposition |
| --- | --- | --- | ---: | --- |
| Addresses and schemes | `py,sh,yml,yaml,json,toml,properties,xml,conf,env,md` | `https?://`, `wss?://`, `jdbc:`, `mongodb://`, `redis://`, `amqp://`, `kafka`, `ldaps?://`, `smtp`, `ftp://`, `sftp`, `file://`, `:[0-9]{4,5}`; hostname pattern `[[:alnum:]_-]+\.(com|net|org|io|internal|example)(\b|:[0-9]+)` in config files | 14 + 0 hostnames | URL/address hits are documented in component pages; no separate hostnames in configuration files |
| Outbound Python | `py` | `requests\.`, `httpx`, `aiohttp`, `urllib`, `grpc\.`, `zeep`, `http\.client`, `http\.request`, `urlopen\(` | 37 | GitHub and catalog/partner calls are traced in component pages; imports/tests are identified there |
| Data stores and file I/O | `py` | `SQLAlchemy`, `sqlite`, `CREATE TABLE`, `ALTER TABLE`, `json\.(load|dump)`, `open\(`, `read_text\(`, `write_text\(`, `write_bytes\(`, `\.write\(` | 27 | Source/workflow state and file operations are documented; network `urlopen` matches are outbound-call false positives |
| Messaging | `py,sh,yml,yaml` | `Kafka`, `Rabbit`, `Jms`, `Sqs`, `PubSub`, `create_issue`, `.comment(`, `workflow_dispatch`, `issue_comment`, `pull_request`, `issues(`, `review` | 46 | GitHub issue, comment, pull-request, and workflow messaging is documented |
| Entry points | `py,sh,yml,yaml` | `main(`, `if __name__`, `argparse`, `workflow_dispatch`, `workflow_call`, `on:`, `make_server`, `BaseHTTPRequestHandler` | 68 | CLI, test, server, and workflow entry points are documented |
| Scheduled/background work | `py,sh,yml,yaml` | `schedule:`, `cron`, `time.sleep`, `sleep(`, `while True`, `BackgroundService`, `Celery`, `threading`, `asyncio.create_task` | 6 | Queue schedule, pagination loop, test-server thread, and the undocumented supplier cron claim are catalogued |
| Configuration and secrets | `py,sh,yml,yaml,json,toml` | `os.environ`, `os.getenv`, `env:`, `secrets.`, `inputs.`, `GH_TOKEN`, `TOKEN`, `PASSWORD`, `SECRET`, `API_KEY` | 38 | Workflow inputs, environment names, and secret references are documented without values |
| Security | `py,sh,yml,yaml,json,toml` | `oauth2`, `jwt`, `Bearer`, `Authorization`, `api_key`, `apikey`, `X-API-Key`, `CORS`, `csrf`, `keystore`, `truststore`, `ssl`, `tls`, `verify=False`, `InsecureSkipVerify`, `permissions:`, `GH_TOKEN`, `shell:`, `subprocess` | 21 | Authorization, workflow permissions, and subprocess behavior are documented |
| Outside programs/files | `py,sh,yml,yaml,json,toml` | `subprocess`, `child_process`, `os.system`, `gh api`, `curl`, `wget`, `sendmail`, `ftp` | 6 | Toolkit subprocesses and the POC `gh api` call are documented |
| Publishing and registries | `py,sh,yml,yaml,json,toml` | `docker push/tag/login`, `REGISTRY`, `REPOSITORY_PREFIX`, `*.azurecr.io`, `ghcr.io`, `*.dkr.ecr.*`, `helm push`, `mvn deploy`, `npm publish`, `twine upload`, artifact repositories | 0 | No publishing or registry flow found |
| Text addressed to an assistant | `py,sh,yml,yaml,json,toml,md,txt` | `AI assistant`, `assistant:`, `Copilot`, `Claude`, `ChatGPT`, `LLM`, `ignore previous/all`, `do not read/mention/report`, `you must`, `instructions to` | 49 | Product terminology and operational task text; exact locations recorded in `run-notes.md` |

- No additional routes or system behaviors needing analysis were found beyond the already documented catalog endpoints, workflow adapters, and fanout-generated instructions.
