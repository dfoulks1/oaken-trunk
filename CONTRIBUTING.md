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
apps/cli/                the `oaken-trunk` command, a thin client (package oaken_trunk_cli)
docs/                    architecture, ADRs, build prompts
```

Core never imports a plugin or a client. A plugin never touches another plugin's storage. Plugins
register through entry points: `oaken_trunk.ingestors`, `oaken_trunk.spools`, `oaken_trunk.senders`.

## AI tooling

Contributions made with generative AI must follow the ASF
[Generative Tooling Guidance](https://www.apache.org/legal/generative-tooling.html), exactly as in
Oaken Mail: you represent the work is yours to license under Apache-2.0, no GPL or incompatible
code, and a provenance trailer (`Co-authored-by:` or `Generated-by:`) in the commit message.
Public-facing AI-written text is reviewed by a committer or labelled as AI-generated.

## Picking up a prompt

Trunk is built from numbered, self-contained prompts in [`docs/prompts/`](docs/prompts/README.md).

1. Read `docs/prompts/00-context.md`, this guide, the ADRs, and the architecture page for your part.
2. Pick a prompt that is **Open** and whose dependencies are **Built**.
3. Start with: *"Read `docs/prompts/00-context.md`, then execute `docs/prompts/NN-....md`."* Where
   a prompt and the code or docs disagree, the code and docs win; stop and report.
4. In the same pull request, update the status table below and `docs/softmap.toml`.

### Status of the prompts

| # | Prompt | Status |
|---|---|---|
| 01 | bootstrap | Written |
| 02 | contracts-and-core | Written |
| 03 | directory-spool | Written |
| 04 | plugin-host | Written |
| 05 | http-ingest | Written |
| 06 | cli-client | Written |
| 07 | lmtp-ingest | Written |
| 08 | consumer-api | Written |
| 09 | smtp-ingest | Written |
| 10 | multi-worker | Written |
| 11 | send | Written |
| 12 | redis-spool | Written |
| 13 | s3-sqs-spool | Written |
| 14 | security-hardening | Written |
| 15 | docs-site | Written |
