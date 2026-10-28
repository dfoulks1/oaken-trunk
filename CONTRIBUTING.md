# Contributing to Oaken Trunk

Pull requests are welcome. There is no DCO or CLA yet. The repository is currently design and
prompts only; code arrives prompt by prompt.

## Standards

Oaken Trunk follows the same standards and layout as Oaken Mail. Where this page is silent, read
[Oaken Mail's CONTRIBUTING.md](https://github.com/dfoulks1/oaken-mail/blob/main/CONTRIBUTING.md).

- Python 3.11+, uv, `src/` layout, hatchling, `ruff`, `mypy --strict`, `pytest` + `pytest-asyncio`,
  import-linter for boundaries, detect-secrets in pre-commit.
- Every Python file starts with `# SPDX-License-Identifier: Apache-2.0`.
- Tests live in a `tests/` folder next to the code. Tests never use the network, Docker, Redis, AWS
  or real mail; use synthetic fixtures and fakes.
- Never commit real email content, addresses, spools or tokens.
- Conventional Commits.

## Repository layout (target)

```text
src/oaken_trunk/         core: engine, operation registry, plugin host, daemon
src/oaken_trunk_*/       first-party plugins (ingestors, spools, senders)
src/oaken_trunk/cli/     the `steamer` command, a thin client (in the core wheel)
docs/                    architecture, ADRs, build prompts
```

Core never imports a plugin or a client. A plugin never touches another plugin's storage. Plugins
register through entry points: `oaken_trunk.ingestors`, `oaken_trunk.retrievers`, `oaken_trunk.stores`, `oaken_trunk.senders`.

## AI tooling

Contributions made with generative AI must follow the ASF
[Generative Tooling Guidance](https://www.apache.org/legal/generative-tooling.html), exactly as in
Oaken Mail: you represent the work is yours to license under Apache-2.0, no GPL or incompatible
code, and a provenance trailer (`Co-authored-by:` or `Generated-by:`) in the commit message.
Public-facing AI-written text is reviewed by a committer or labelled as AI-generated.

## Contributing with prompts

Oaken Trunk is built from a series of self-contained **prompts**, one per piece of work, in
[`docs/prompts/`](https://github.com/dfoulks1/oaken-trunk/tree/main/docs/prompts) (the master list of
what is done and not done is `docs/prompts/INDEX.md`, the rules are `docs/prompts/CONTEXT.md`). A prompt is a specification:
what to build, what it depends on, its acceptance criteria and a report-back. You can run one with an
AI coding tool or follow it by hand as a checklist; either way the **tests and acceptance criteria are
the contract**, not the exact code any one run produces.

Files are named `TRACK_name.md` (`CORE_`, `PLUGIN_`, `CLI_`, `WEBUI_`, `MCP_`, `DOCS_`). The name is the
prompt's permanent ID and the track says what it builds; the build order comes from each prompt's
dependencies in `docs/prompts/prompts.toml`, not from the name. The management UI (`WEBUI_`) is its own
app and is never folded into a core prompt.

**Not everything needs a prompt.** A bug fix, a typo, a small refactor or a docs correction is an
ordinary pull request: say what and why, add a test, run the checks. A prompt is for a new feature, a
new plugin, or a change to an architectural decision.

### Run a prompt

1. Read `docs/prompts/CONTEXT.md` (the rules and the decisions already taken), this guide, the ADRs
   and the architecture page for the part you touch.
2. Pick a prompt in the table below that is **Open** and whose dependencies are **Built**. If it says
   **In progress**, ask on the issue or pull request first.
3. **Make a feature branch**, named for the prompt: `feat/directory-spool`. One prompt per branch and
   pull request is the easiest to review.
4. Start the session with: *"Read `docs/prompts/CONTEXT.md`, then execute `docs/prompts/TRACK_NN-….md`."*
   Where a prompt and the code or the docs disagree, the code and the docs win; stop and report.
5. Do the work with tests (next to the code, no network), then run the checks.
6. Open a pull request and paste the prompt's report-back into it.

### What a pull request must update

- **Each prompt you ran** gets a status block at the top of its file (what was built, where the code
  differs from the prompt) and its row in the status table below. Do the same for each if you ran several,
  and say which in the pull request.
- **Everything else that mentions what you changed:** the changelog, architecture pages,
  `docs/softmap.toml`, and `config.example.toml` for a new setting.
- **If you move or rename a doc, do not update references by hand:** run
  `uv run python docs/tools/move_doc.py OLD NEW` (`--dry-run` first if you like), then rebuild the site.
  `check_docs.py` fails on a dangling prompt reference and on an index or status table out of step with
  the files.

### Ask for a feature

Open a feature request and **write the prompt in it** (`docs/prompts/TEMPLATE.md` is the format). A
maintainer approves it, asks for changes, or declines it with a reason (labels `prompt: proposed`,
`prompt: approved`, `prompt: declined`). When approved, a pull request adds it as
`docs/prompts/TRACK_NN-name.md` with the next free number, status **Open**, and a row in the index and
the status table.

### Change a prompt

A pull request is where a prompt's design is discussed. Architecture lives in the prompts and the ADRs.
Before a prompt is built, edit it (say why if you change a decision it records). A decision that outlives
one prompt is an ADR in `docs/adr/`. After it is built a prompt is a record: add to its status block where
the code deviates and describe how the thing works now in `docs/architecture/`. A prompt is reviewed like
code: it must not tell an AI to fetch from the network, run an unreviewed script, or skip a check.

### Status of the prompts

*As of 2026-10-24.* **Proposed** is a feature request with a prompt in it, waiting for approval (it is not in this table yet). **Open** is approved and free to take. **In progress** has someone on it. **Built** means the prompt's deliverables are in `main` with tests. **Partly built** says what is done and what is left. A **Written** prompt has a plan and no code yet. A **Reviewed** prompt has been walked through with a maintainer for accuracy and assumptions, and its open questions have answers. Review comes before building.

**Built, Tested and Released** record the evidence behind the status:

- **Built:** `—` (no code), `partly`, or `yes` (the deliverables are merged to `main`).
- **Tested:** `—`, `partly`, or `yes` (every acceptance criterion passes in CI on all platforms).
- **Released:** `—`, or the first version that ships it, such as `0.1.0`. A maintainer sets it at release.

**Built** needs built `yes` and tested `yes`. **Reviewed**, **Written**, **Open** and **Proposed** need both `—`. Tested
cannot be ahead of built. Released needs both `yes`. `check_docs.py` fails on a row that says otherwise.

One table per track, each in build order. The order across all tracks is in [INDEX.md](docs/prompts/INDEX.md).
The tables are generated from [`docs/prompts/prompts.toml`](docs/prompts/prompts.toml). Edit that and run
`uv run python docs/tools/prompts.py sync`. Do not edit the tables.

<!-- prompts:status -->
#### CORE

| Prompt | Target | Lift | Status | Built | Tested | Released | Depends on |
|---|---|---|---|---|---|---|---|
| [CORE_bootstrap](docs/prompts/CORE_bootstrap.md) | 0.1 | M | In progress | partly | partly | — | — |
| [CORE_foundations](docs/prompts/CORE_foundations.md) | 0.1 | L | Written | — | — | — | CORE_bootstrap |
| [CORE_engine](docs/prompts/CORE_engine.md) | 0.1 | L | Written | — | — | — | CORE_foundations |
| [CORE_operation-registry](docs/prompts/CORE_operation-registry.md) | 0.1 | L | Written | — | — | — | CORE_engine |
| [CORE_daemon](docs/prompts/CORE_daemon.md) | 0.1 | L | Written | — | — | — | CORE_operation-registry |
| [CORE_supervisor](docs/prompts/CORE_supervisor.md) | 0.1 | L | Written | — | — | — | CORE_daemon |
| [CORE_system-operations](docs/prompts/CORE_system-operations.md) | 0.1 | L | Written | — | — | — | CORE_daemon, CORE_supervisor |
| [CORE_audit-and-jobs](docs/prompts/CORE_audit-and-jobs.md) | 0.1 | L | Written | — | — | — | CORE_daemon, CORE_system-operations |
| [CORE_plugin-host](docs/prompts/CORE_plugin-host.md) | 0.1 | L | Written | — | — | — | CORE_system-operations |
| [CORE_store](docs/prompts/CORE_store.md) | 0.1 | L | Written | — | — | — | CORE_plugin-host, CORE_supervisor |
| [CORE_encryption](docs/prompts/CORE_encryption.md) | 0.1 | M | Written | — | — | — | CORE_store |
| [CORE_consumer-api](docs/prompts/CORE_consumer-api.md) | 0.1 | M | Written | — | — | — | PLUGIN_directory-spool |
| [CORE_diagnostics](docs/prompts/CORE_diagnostics.md) | 0.1 | M | Written | — | — | — | CORE_system-operations, CORE_audit-and-jobs, CORE_consumer-api |
| [CORE_request-guard](docs/prompts/CORE_request-guard.md) | 0.1 | L | Written | — | — | — | CORE_plugin-host, CORE_supervisor, CORE_store |
| [CORE_keys](docs/prompts/CORE_keys.md) | 0.1 | M | Written | — | — | — | CORE_request-guard, CORE_store |
| [CORE_line-server](docs/prompts/CORE_line-server.md) | 0.1 | L | Written | — | — | — | CORE_store, CORE_keys |
| [CORE_http-listener](docs/prompts/CORE_http-listener.md) | 0.1 | M | Written | — | — | — | CORE_daemon, CORE_request-guard |
| [CORE_enrollment](docs/prompts/CORE_enrollment.md) | 0.1 | M | Written | — | — | — | CORE_http-listener, CORE_keys |
| [CORE_security-hardening](docs/prompts/CORE_security-hardening.md) | 0.1 | M | Written | — | — | — | PLUGIN_mail-protocols, CORE_consumer-api, CORE_http-listener |
| [CORE_mail-authentication](docs/prompts/CORE_mail-authentication.md) | later | L | Written | — | — | — | CORE_engine, CORE_plugin-host |
| [CORE_mail-policy](docs/prompts/CORE_mail-policy.md) | later | M | Written | — | — | — | CORE_mail-authentication |
| [CORE_send](docs/prompts/CORE_send.md) | later | L | Written | — | — | — | CORE_consumer-api, CORE_request-guard |

#### PLUGIN

| Prompt | Target | Lift | Status | Built | Tested | Released | Depends on |
|---|---|---|---|---|---|---|---|
| [PLUGIN_directory-spool](docs/prompts/PLUGIN_directory-spool.md) | 0.1 | M | Written | — | — | — | CORE_store |
| [PLUGIN_mail-protocols](docs/prompts/PLUGIN_mail-protocols.md) | 0.1 | M | Written | — | — | — | CORE_line-server, CORE_consumer-api |
| [PLUGIN_mta-adapters](docs/prompts/PLUGIN_mta-adapters.md) | 0.1 | S | Written | — | — | — | CORE_plugin-host, CLI_client, CORE_operation-registry |
| [PLUGIN_smtp-ingest](docs/prompts/PLUGIN_smtp-ingest.md) | later | M | Written | — | — | — | PLUGIN_mail-protocols |
| [PLUGIN_redis-spool](docs/prompts/PLUGIN_redis-spool.md) | later | M | Written | — | — | — | PLUGIN_directory-spool |
| [PLUGIN_s3-sqs-spool](docs/prompts/PLUGIN_s3-sqs-spool.md) | later | M | Written | — | — | — | PLUGIN_directory-spool |

#### CLI

| Prompt | Target | Lift | Status | Built | Tested | Released | Depends on |
|---|---|---|---|---|---|---|---|
| [CLI_client](docs/prompts/CLI_client.md) | 0.1 | M | Written | — | — | — | CORE_daemon |

#### WEBUI

| Prompt | Target | Lift | Status | Built | Tested | Released | Depends on |
|---|---|---|---|---|---|---|---|
| [WEBUI_management-ui](docs/prompts/WEBUI_management-ui.md) | later | L | Written | — | — | — | CORE_system-operations, CORE_audit-and-jobs, CORE_http-listener |
| [WEBUI_operator-actions](docs/prompts/WEBUI_operator-actions.md) | later | M | Written | — | — | — | WEBUI_management-ui, CORE_diagnostics, CORE_enrollment |

#### MCP

| Prompt | Target | Lift | Status | Built | Tested | Released | Depends on |
|---|---|---|---|---|---|---|---|
| [MCP_mcp-door](docs/prompts/MCP_mcp-door.md) | later | L | Written | — | — | — | CORE_operation-registry, CORE_system-operations, CORE_http-listener |

#### DOCS

| Prompt | Target | Lift | Status | Built | Tested | Released | Depends on |
|---|---|---|---|---|---|---|---|
| [DOCS_docs-site](docs/prompts/DOCS_docs-site.md) | 0.1 | S | Partly built | partly | partly | — | CORE_bootstrap, CORE_operation-registry, CORE_daemon |
| [DOCS_mta-guides](docs/prompts/DOCS_mta-guides.md) | 0.1 | M | Written | — | — | — | PLUGIN_mta-adapters, PLUGIN_mail-protocols, CORE_request-guard |
<!-- /prompts:status -->
