# Bootstrap: the workspace, the tooling and CI

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/CORE.md`.
**Depends on:** nothing.
**Track:** `CORE_`. It creates the empty packages and the checks; it adds no gateway behaviour.
**Delivers:** uv workspace, tooling, legal files, a green empty project

## Goal

A green, empty project: one command installs it, one command checks it, `steamer --version`
prints the version, and CI proves it on Linux, macOS and Windows. Nothing here receives mail.

## Decisions already taken (do not re-litigate)

- **Packaging.** The `oaken-trunk` wheel is the *core*: the ingestion pipeline (engine, operation
  registry, plugin host, daemon) **and** the `steamer` command, which is a thin client. The wheel
  also ships one **default plugin set** so a bare install works. Heavy plugins (Redis, S3+SQS, and
  anything that pulls in a large dependency) are **separate packages** in the same workspace, each
  with its own `pyproject.toml`, installed on demand. A third party packages a plugin the same way.
- **Platforms.** CI runs Linux, macOS and Windows on Python 3.11, 3.12 and 3.13. Where a feature
  cannot exist on a platform, the code says so and the test is skipped with a stated reason; it is
  never silently absent. (See the open questions for what that means per feature.)
- **Actions are pinned by full commit SHA**, with the tag in a trailing comment, and Dependabot
  keeps them current (ASF policy).
- **The docs tooling already exists** (`docs/tools`, built under DOCS_docs-site). This prompt folds it into the new
  root `pyproject.toml` as the `docs` dependency group; its tests stay in `docs/tools/tests`.
  The gateway's runtime never depends on that group. DOCS_docs-site is "Partly built" because of this.
- Standards are those in `CONTRIBUTING.md`: Python 3.11+, uv, hatchling, `src/` layout, tests in a
  `tests/` folder next to the code, SPDX header on every Python file.

## Not in scope

Any engine, spool, ingestor, API or CLI verb other than `--version` (CORE_contracts-and-core onward); releases,
a container image and distribution packages (not planned yet, see ROADMAP); the docs site (DOCS_docs-site).

## Requirements

1. **Workspace.** Root package `oaken-trunk` with `src/oaken_trunk/__init__.py` holding `__version__`
   and nothing else. The CLI lives in the wheel as `oaken_trunk.cli` with the console script
   `steamer = "oaken_trunk.cli:main"`, using only the standard library (argparse, lazy imports)
   so `--version` starts fast. The workspace lists the heavy-plugin packages as members as they are
   added; this prompt adds none.
2. **One version.** `__version__` is the single source: hatch reads it (`[tool.hatch.version] path`)
   and no other file states it. A test fails if any workspace member or `CHANGELOG.md` disagrees.
3. **Lint, types, tests.** `ruff` (E, F, I, UP, B, ASYNC, S, line length 100), `mypy --strict`,
   `pytest` with `pytest-asyncio`, `import-linter`.
4. **Import contracts**, written as import-linter contracts, each with a test that a violation is
   caught: core never imports a plugin or a client; a plugin never imports another plugin; nothing
   imports `oaken_trunk.testing` outside tests.
5. **SPDX.** Every `.py` file starts with `# SPDX-License-Identifier: Apache-2.0`; a hand-written
   check fails otherwise (not a ruff rule, so it does not depend on a preview feature).
6. **Test isolation.** The root `conftest.py` gives every test its own `OAKEN_TRUNK_HOME` (a temp
   dir) and removes every other `OAKEN_TRUNK_*` variable from the environment.
7. **Repo-wide tests** in `tests/`: no tracked file matches a sensitive pattern (`*.db`, `*.eml`,
   `*.mbox`, `.env*` except `.env.example`, `*.pem`, `*.key`, DKIM or signing keys, `token*.json`,
   `credentials*.json`, `config.toml`, anything under a spool directory); `.gitignore` covers each
   pattern (assert it with `git check-ignore`); the version test (requirement 2).
8. **Secret scanning.** `pre-commit` with ruff, mypy and detect-secrets, a committed
   `.secrets.baseline`, and the same scan as a CI job.
9. **CI** (`.github/workflows/ci.yml`): Linux, macOS, Windows × Python 3.11, 3.12, 3.13, running
   `uv sync --locked`, `ruff check`, `ruff format --check`, `mypy`, `lint-imports`, `pytest`; plus the
   secret-scan job and the docs check (`docs/tools/check_docs.py`). Actions pinned as decided.
   Workflow `permissions:` default to `contents: read`.
10. **Test fixtures for synthetic mail** in `oaken_trunk.testing`: a few small, clearly fake RFC 5322
    messages (plain, multipart, oversized-header, truncated) and a helper that yields a message as a
    stream of fixed-size chunks. Every later ingestor, spool and consumer test uses these; no real
    mail, address or domain other than `example.org` appears anywhere.
11. **`steamer --version`** prints the version and exits 0; `python -m oaken_trunk` does the same.

## Acceptance criteria

- On a fresh clone, `uv sync --locked`, then `ruff check`, `ruff format --check`, `mypy`,
  `lint-imports` and `pytest` all pass, with no network, Docker or real mail used by any test.
- `steamer --version` and `python -m oaken_trunk` print the same version, which is the one in
  `src/oaken_trunk/__init__.py`.
- Changing the version in a second place makes the version test fail; adding `import oaken_trunk_x`
  to core, or one plugin importing another, makes `lint-imports` fail; deleting an SPDX header makes
  the SPDX check fail; staging a `*.pem` or a `config.toml` makes the repo-wide test fail.
- `.github/workflows/ci.yml` contains no `uses:` reference that is not a 40-character SHA.
- `docs/tools/check_docs.py` and its tests still pass, and the `docs` group is not a runtime
  dependency of `oaken-trunk` (assert it from the built metadata).
- The status table in `CONTRIBUTING.md`, `docs/softmap.toml` and the README's status line are updated.

## Open questions (defaults in bold)

1. **What is the default plugin set in the core wheel?** **Directory spool, HTTP ingest, CLI stdin
   submit.** LMTP and SMTP are also in the wheel only if they add no dependency; otherwise they are
   separate packages. (Decide before PLUGIN_directory-spool.)
2. **What does "supported on Windows" mean?** **Core, CLI, directory spool and HTTP ingest run and are
   tested on Windows; LMTP over a Unix socket with peer credentials, multi-worker `SO_REUSEPORT`,
   and inotify notification are Linux/macOS only, with the polling fallback used on Windows.** A
   production Postfix host is Linux in practice.
3. **Do the heavy plugins share one version with core?** **Yes, released in lockstep until 1.0.**

## Report-back checkpoint

End with the report sections from `CONTEXT.md`, listing which open questions you took the default
on. Then stop.
