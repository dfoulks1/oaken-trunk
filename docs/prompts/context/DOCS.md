# Context: DOCS_ prompts

Read with [CONTEXT.md](../CONTEXT.md). The docs site and public docs.

- **Tooling is `docs/tools`.** `build_site.py` builds. `check_docs.py` fails on broken links, anchors and
  hosts, non-deterministic output, stale generated HTML, and a prompt series out of step.
  `scripts/check.sh` runs it all.
- **`docs/softmap.toml`** says what is built, partial or planned. Never claim more.
- **`docs/prompts/prompts.toml`** is the prompt manifest. Edit it, then run `prompts.py sync`.
- **Move a doc with `docs/tools/move_doc.py`,** never by hand.
- Generated HTML is committed. Never edit or read it in a prompt session.
- Public AI-written text is reviewed or labelled (see CONTRIBUTING).
