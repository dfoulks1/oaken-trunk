# Changelog

All notable changes are listed here. The format follows Keep a Changelog.

## [Unreleased]

- Design, architecture decisions and the build-prompt series.
- Workspace and tooling (CORE_bootstrap): the `oaken-trunk` package with `steamer --version`,
  ruff, mypy, pytest, import-linter contracts, an SPDX check, repo-wide guards against tracked
  mail or secrets, synthetic test mail in `oaken_trunk.testing`, and pre-commit with detect-secrets.
- Foundations and contracts (CORE_foundations): paths, strict settings (pydantic-settings),
  the envelope, time-ordered message ids, the error table, and the `Spool`, `Ingestor`, listener
  event and `Credits` contracts with `FakeSpool`, `FakeIngestor` and `RecordingListenerHost`.
