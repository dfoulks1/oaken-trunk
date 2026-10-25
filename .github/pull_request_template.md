## What and why

<!-- Which prompt(s) does this run? e.g. CORE_engine. A small fix needs none. -->

**Prompts covered:**

## Checklist

- [ ] Tests added or updated, next to the code, with no network
- [ ] `uv run ruff check`, `ruff format --check`, `mypy`, `lint-imports` and `pytest` pass
- [ ] Docs updated; `uv run --group docs python docs/tools/check_docs.py` passes
- [ ] On a feature branch named for the prompt (`feat/directory-spool`); each prompt run has a status block at the top of its file and its row updated in `CONTRIBUTING.md`
- [ ] A moved or renamed doc went through `docs/tools/move_doc.py`
- [ ] No real mail, tokens or personal addresses in fixtures or logs
- [ ] A change to an operation or plugin contract regenerated its snapshot and says why (ADR 0010)
