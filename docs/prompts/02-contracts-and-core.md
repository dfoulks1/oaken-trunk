# 02 - Contracts and core

**Read first:** `docs/prompts/00-context.md`. **Depends on:** 01.

## Goal

The Ingestor, Spool and Sender contracts, settings, paths, errors, and the engine that streams a message into a spool under limits.

## Steps

1. `core/paths.py`: `OAKEN_TRUNK_HOME` (`<dir>/config`, `<dir>/data`), platformdirs default, owner-only directories, last-known-home pointer as oaken-mail does.
2. `core/settings.py`: pydantic settings; defaults < `config.toml` < `OAKEN_TRUNK_*`; unknown top-level keys are an error; sizes like `25MiB`; the `[server]` limits in `config.example.toml`.
3. Contracts per `docs/architecture/spool.md` and `ingestion.md`; typed errors for each backpressure condition mapped to SMTP and HTTP codes.
4. Engine: assign a time-ordered message id, stream chunks (64 KiB) with a size cap, enforce `max_inflight` (global, split per worker) and `max_spool_bytes`, never buffer a whole message.
5. A `FakeSpool`, `FakeIngestor` and `FakeSender`. The contract dataclasses live here; the base classes and contract suites are built in prompt 04.

## Acceptance criteria

- A test streams a message larger than RAM-per-chunk through the engine into `FakeSpool` and observes peak chunk size, size-cap rejection, and 4xx on overload.
- `ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass; no network, Docker or real mail in tests.
- Docs and `docs/softmap.toml` updated; the status table in `CONTRIBUTING.md` updated.

## Checkpoint

Use the report format from `00-context.md`, then stop.
