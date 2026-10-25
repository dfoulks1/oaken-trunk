# SPDX-License-Identifier: Apache-2.0
"""The prompt manifest tool: what it generates, and each way a prompt tree goes wrong."""

from pathlib import Path

import prompts
from model import load_config
from render import link_prompt_names

ROOT = Path(__file__).resolve().parents[3]


def entry(name: str, depends: list[str] | None = None, **kw: str) -> str:
    f = {"status": "Written", "built": "—", "tested": "—", "released": "—", "target": "0.1", **kw}
    deps = ", ".join(f'"{d}"' for d in depends or [])
    body = "".join(f'{k} = "{v}"\n' for k, v in f.items())
    return f'[[prompt]]\nname = "{name}"\ndepends = [{deps}]\n{body}\n'


def tree(tmp: Path, entries: list[str], files: dict[str, str] | None = None) -> Path:
    def put(rel: str, text: str) -> None:
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    put("docs/prompts/prompts.toml", "".join(entries))
    block = "<!-- prompts:{0} -->\nx\n<!-- /prompts:{0} -->\n"
    put("docs/prompts/INDEX.md", block.format("master") + block.format("order"))
    put("CONTRIBUTING.md", block.format("status"))
    put("docs/prompts/context/CORE.md", "core\n")
    for e in entries:
        name = e.split('name = "')[1].split('"')[0]
        put(
            f"docs/prompts/{name}.md",
            "# t\n\n**Read first:** `docs/prompts/context/CORE.md`.\n**Depends on:** x\n"
            f"**Lift:** M\n**Delivers:** does {name}\n",
        )
    for rel, text in (files or {}).items():
        put(rel, text)
    prompts.sync(tmp)
    return tmp


def two(tmp: Path) -> Path:
    return tree(tmp, [entry("CORE_a"), entry("CORE_b", ["CORE_a"])])


def test_a_consistent_tree_passes_and_sync_writes_the_generated_parts(tmp_path: Path) -> None:
    r = two(tmp_path)
    assert prompts.problems(r) == []
    assert "[CORE_a](CORE_a.md)" in (r / "docs/prompts/CORE_b.md").read_text()
    assert "does CORE_a" in (r / "docs/prompts/INDEX.md").read_text()
    assert "| [CORE_b](docs/prompts/CORE_b.md) | 0.1 | M | Written" in (r / "CONTRIBUTING.md").read_text()


def test_build_order_puts_dependencies_first_and_target_01_before_later(tmp_path: Path) -> None:
    r = tree(
        tmp_path,
        [entry("CORE_late", target="later"), entry("CORE_b", ["CORE_a"]), entry("CORE_a")],
    )
    names = [p.name for p in prompts.order(prompts.load(r))]
    assert names == ["CORE_a", "CORE_b", "CORE_late"]


def test_each_way_a_tree_goes_wrong(tmp_path: Path) -> None:
    cases = {
        "missing": (
            [entry("CORE_a", ["CORE_ghost"])],
            "depends on CORE_ghost, which is not in prompts.toml",
        ),
        "cycle": (
            [entry("CORE_a", ["CORE_b"]), entry("CORE_b", ["CORE_a"])],
            "dependency cycle",
        ),
        "later": (
            [entry("CORE_a", ["CORE_b"]), entry("CORE_b", target="later")],
            "is target 0.1 but depends on CORE_b",
        ),
        "status": ([entry("CORE_a", status="Done")], "status 'Done' is not one of"),
    }
    for sub, (entries, want) in cases.items():
        (tmp_path / sub).mkdir()
        got = "\n".join(prompts.problems(tree(tmp_path / sub, entries)))
        assert want in got, (sub, got)


def test_stale_output_unknown_names_and_missing_pieces_are_named(tmp_path: Path) -> None:
    r = two(tmp_path)
    (r / "docs/prompts/CORE_b.md").write_text(
        "# t\n**Read first:** nothing.\n**Depends on:** [CORE_zzz](CORE_zzz.md).\n"
    )
    (r / "docs/notes.md").write_text("see CORE_gone-away and CORE_02-old\n")
    (r / "docs/prompts/CORE_orphan.md").write_text("# o\n")
    got = "\n".join(prompts.problems(r))
    assert "CORE_b.md is out of date" in got
    assert "docs/prompts/CORE_b.md has no **Delivers:** line" in got
    assert "CORE_b does not name docs/prompts/context/CORE.md" in got
    assert "docs/notes.md mentions CORE_gone-away, which is not a prompt" in got
    assert "docs/notes.md mentions CORE_02-old, which is not a prompt" in got
    assert "docs/prompts/CORE_orphan.md is not in prompts.toml" in got


def test_milestone_columns_must_agree_with_status(tmp_path: Path) -> None:
    def run(sub: str, **kw: str) -> str:
        (tmp_path / sub).mkdir()
        return "\n".join(prompts.problems(tree(tmp_path / sub, [entry("CORE_a", **kw)])))

    assert run("ok", status="Built", built="yes", tested="yes", released="0.1.0") == ""
    assert "tested is ahead of built" in run("a", status="Partly built", built="partly", tested="yes")
    assert "released needs built and tested yes" in run(
        "b", status="Built", built="yes", tested="partly", released="0.1.0"
    )
    assert "Written but built or tested is set" in run("c", built="yes")
    assert "Built needs built and tested yes" in run("d", status="Built", built="yes")
    assert "released is — or a version" in run(
        "e", status="Built", built="yes", tested="yes", released="soon"
    )


def test_a_plain_prompt_name_in_a_page_becomes_a_link(tmp_path: Path) -> None:
    r = two(tmp_path)
    cfg = load_config(ROOT / "docs", ROOT)
    cfg = type(cfg)(**{**cfg.__dict__, "docs_dir": r / "docs", "repo_root": r})
    text = "Build CORE_a then `CORE_b`, not CORE_nope.\n\n```\nCORE_a\n```\n[x](CORE_a.md)\n"
    out = link_prompt_names(text, cfg)
    assert "[CORE_a](repo:docs/prompts/CORE_a.md)" in out
    assert "[`CORE_b`](repo:docs/prompts/CORE_b.md)" in out
    assert "CORE_nope" in out and "[CORE_nope]" not in out
    assert "```\nCORE_a\n```" in out and "[x](CORE_a.md)" in out


def test_the_real_prompt_tree_is_consistent() -> None:
    assert prompts.problems(ROOT) == []
