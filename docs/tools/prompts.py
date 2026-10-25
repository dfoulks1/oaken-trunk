#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The prompt manifest: identity, dependencies and status in one file, the rest generated.

    uv run python docs/tools/prompts.py sync     rewrite every generated block
    uv run python docs/tools/prompts.py check    list what is out of step (check_docs runs this)

``docs/prompts/prompts.toml`` holds each prompt's name, depends, status, built, tested, released and
target. Content stays in the prompt's own file (``docs/prompts/<name>.md``, with a ``**Delivers:**``
line). Sync writes: each file's ``**Depends on:**`` line, the master list and build order in
``INDEX.md``, and the status table in ``CONTRIBUTING.md``, between ``<!-- prompts:TAG -->`` markers.
"""

import re
import subprocess  # noqa: S404 (git ls-files, a fixed command)
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

TRACKS = ("CORE", "PLUGIN", "CLI", "WEBUI", "MCP", "DOCS")
NAME = re.compile(rf"^(?:{'|'.join(TRACKS)})_[a-z0-9]+(?:-[a-z0-9]+)*$")
MENTION = re.compile(rf"(?<![A-Za-z0-9_])((?:{'|'.join(TRACKS)})_[a-z0-9]+(?:-[a-z0-9]+)*)")
STATUSES = ("Proposed", "Open", "Written", "In progress", "Partly built", "Built")
LEVELS = {"—": 0, "partly": 1, "yes": 2}
LIFTS = ("S", "M", "L", "XL")
RESERVED = {"CONTEXT.md", "INDEX.md", "README.md", "TEMPLATE.md"}
TEXT = {".md", ".py", ".toml", ".json", ".yml", ".yaml", ".txt"}


@dataclass
class Prompt:
    name: str
    depends: list[str]
    status: str
    built: str
    tested: str
    released: str
    target: str = "later"


@dataclass
class Manifest:
    prompts: list[Prompt] = field(default_factory=list)
    retired: dict[str, str] = field(default_factory=dict)  # name -> merged_into

    def names(self) -> set[str]:
        return {p.name for p in self.prompts}


def load(root: Path) -> Manifest:
    data = tomllib.loads((root / "docs/prompts/prompts.toml").read_text("utf-8"))
    m = Manifest()
    for e in data.get("prompt", []):
        m.prompts.append(
            Prompt(e["name"], list(e.get("depends", [])), e["status"], e["built"], e["tested"],
                   e["released"], e.get("target", "later"))  # fmt: skip
        )
    for e in data.get("retired", []):
        m.retired[e["name"]] = e["merged_into"]
    return m


def delivers(root: Path, name: str) -> str:
    text = (root / "docs/prompts" / f"{name}.md").read_text("utf-8")
    hit = re.search(r"^\*\*Delivers:\*\* (.+)$", text, re.M)
    return hit.group(1).strip() if hit else ""


def lift(root: Path, name: str) -> str:
    text = (root / "docs/prompts" / f"{name}.md").read_text("utf-8")
    hit = re.search(r"^\*\*Lift:\*\* (\S+)\s*$", text, re.M)
    return hit.group(1) if hit else ""


def order(m: Manifest) -> list[Prompt]:
    """Dependencies first. Target 0.1 before later; ties keep manifest order."""
    by = {p.name: p for p in m.prompts}
    done: list[Prompt] = []
    placed: set[str] = set()
    rank = {"0.1": 0}
    pending = sorted(m.prompts, key=lambda p: rank.get(p.target, 1))
    while pending:
        ready = [p for p in pending if all(d in placed or d not in by for d in p.depends)]
        if not ready:
            break  # a cycle; problems() reports it
        pick = ready[0]
        done.append(pick)
        placed.add(pick.name)
        pending.remove(pick)
    return done + pending


def _list(names: list[str]) -> str:
    return ", ".join(names) if names else "nothing"


def render_master(m: Manifest, root: Path) -> str:
    rows = ["| Prompt | Status | Target | Lift | Delivers | Depends on |", "|---|---|---|---|---|---|"]
    for p in m.prompts:
        rows.append(
            f"| [{p.name}]({p.name}.md) | {p.status} | {p.target} | {lift(root, p.name)} | {delivers(root, p.name)} | "
            f"{', '.join(p.depends) or '—'} |"
        )
    return "\n".join(rows)


def render_status(m: Manifest) -> str:
    rows = ["| Prompt | Status | Built | Tested | Released | Depends on |", "|---|---|---|---|---|---|"]
    for p in m.prompts:
        rows.append(
            f"| [{p.name}](docs/prompts/{p.name}.md) | {p.status} | {p.built} | {p.tested} | "
            f"{p.released} | {', '.join(p.depends) or '—'} |"
        )
    return "\n".join(rows)


def render_order(m: Manifest) -> str:
    out: list[str] = []
    group = None
    for i, p in enumerate(order(m), 1):
        if p.target != group:
            group = p.target
            out.append(("" if not out else "\n") + f"**Target {group}**\n")
        out.append(f"{i}. [{p.name}]({p.name}.md)")
    return "\n".join(out)


BLOCKS = {  # file -> tag -> renderer(manifest, root)
    "docs/prompts/INDEX.md": {"master": render_master, "order": lambda m, r: render_order(m)},
    "CONTRIBUTING.md": {"status": lambda m, r: render_status(m)},
}


def _block(text: str, tag: str, body: str) -> str | None:
    pat = re.compile(rf"(<!-- prompts:{tag} -->\n).*?(\n<!-- /prompts:{tag} -->)", re.S)
    if not pat.search(text):
        return None
    return pat.sub(lambda mo: mo.group(1) + body + mo.group(2), text, count=1)


def depends_line(p: Prompt) -> str:
    links = ", ".join(f"[{d}]({d}.md)" for d in p.depends)
    return f"**Depends on:** {links}." if links else "**Depends on:** nothing."


def _expected(root: Path, m: Manifest) -> dict[Path, str]:
    out: dict[Path, str] = {}
    for p in m.prompts:
        f = root / "docs/prompts" / f"{p.name}.md"
        if f.is_file():
            out[f] = re.sub(r"^\*\*Depends on:\*\*.*$", lambda _: depends_line(p),
                            f.read_text("utf-8"), count=1, flags=re.M)  # fmt: skip
    for rel, tags in BLOCKS.items():
        f = root / rel
        if f.is_file():
            text = f.read_text("utf-8")
            for tag, render in tags.items():
                text = _block(text, tag, render(m, root)) or text
            out[f] = text
    return out


def sync(root: Path) -> int:
    m = load(root)
    n = 0
    for f, text in _expected(root, m).items():
        if f.read_text("utf-8") != text:
            f.write_text(text, encoding="utf-8")
            n += 1
    return n


def _tracked(root: Path) -> list[Path]:
    try:
        out = subprocess.run(  # noqa: S603, S607
            ["git", "ls-files", "-co", "--exclude-standard"], cwd=root,
            capture_output=True, text=True, check=True,
        ).stdout.split("\n")  # fmt: skip
        names = [n for n in out if n]
    except (OSError, subprocess.CalledProcessError):
        names = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()]
    return [
        root / n for n in names
        if Path(n).suffix in TEXT and n != "uv.lock" and not n.startswith((".venv/", "docs/tools/"))
        and (root / n).is_file()
    ]  # fmt: skip


def problems(root: Path) -> list[str]:  # noqa: C901
    if not (root / "docs/prompts/prompts.toml").is_file():
        return []
    m = load(root)
    out: list[str] = []
    pdir = root / "docs/prompts"
    names = [p.name for p in m.prompts]
    for n in sorted({x for x in names if names.count(x) > 1}):
        out.append(f"prompts.toml lists {n} twice")
    known = m.names() | set(m.retired)
    for p in m.prompts:
        if not NAME.match(p.name):
            out.append(f"prompts.toml: {p.name!r} is not TRACK_name (tracks: {', '.join(TRACKS)})")
        if not (pdir / f"{p.name}.md").is_file():
            out.append(f"prompts.toml lists {p.name}, which has no file docs/prompts/{p.name}.md")
        elif not delivers(root, p.name):
            out.append(f"docs/prompts/{p.name}.md has no **Delivers:** line")
        elif lift(root, p.name) not in LIFTS:
            out.append(f"docs/prompts/{p.name}.md needs a **Lift:** line ({'/'.join(LIFTS)})")
        for d in p.depends:
            if d not in m.names():
                out.append(f"{p.name} depends on {d}, which is not in prompts.toml")
            elif d == p.name:
                out.append(f"{p.name} depends on itself")
        if p.status not in STATUSES:
            out.append(f"{p.name}: status {p.status!r} is not one of {', '.join(STATUSES)}")
        out += _milestones(p)
    for f in sorted(pdir.glob("*.md")):
        if f.name not in RESERVED and f.stem not in m.names():
            out.append(f"docs/prompts/{f.name} is not in prompts.toml")
    by = {p.name: p for p in m.prompts}
    for p in m.prompts:
        for d in p.depends:
            if d in by and p.target == "0.1" and by[d].target != "0.1":
                out.append(f"{p.name} is target 0.1 but depends on {d}, which is {by[d].target}")
    if len(order(m)) and {q.name for q in order(m)} != m.names() or _cycle(m):
        out.append("prompts.toml has a dependency cycle")
    tracks = {p.name.split("_")[0] for p in m.prompts}
    if (pdir / "context").is_dir():
        for t in sorted(tracks):
            f = pdir / "context" / f"{t}.md"
            if not f.is_file():
                out.append(f"docs/prompts/context/{t}.md is missing")
        for p in m.prompts:
            f = pdir / f"{p.name}.md"
            t = p.name.split("_")[0]
            if f.is_file() and f"context/{t}.md" not in f.read_text("utf-8"):
                out.append(f"{p.name} does not name docs/prompts/context/{t}.md in Read first")
    for f, want in _expected(root, m).items():
        if f.read_text("utf-8") != want:
            out.append(f"{f.relative_to(root)} is out of date; run: uv run python docs/tools/prompts.py sync")
    for rel, tags in BLOCKS.items():
        text = (root / rel).read_text("utf-8") if (root / rel).is_file() else ""
        for tag in tags:
            if f"<!-- prompts:{tag} -->" not in text:
                out.append(f"{rel} has no <!-- prompts:{tag} --> block")
    for f in _tracked(root):
        for name in sorted(set(MENTION.findall(f.read_text("utf-8", errors="replace")))):
            if name not in known:
                out.append(f"{f.relative_to(root)} mentions {name}, which is not a prompt")
    return out


def _cycle(m: Manifest) -> bool:
    by = {p.name: p for p in m.prompts}
    state: dict[str, int] = {}

    def visit(n: str) -> bool:
        if state.get(n) == 1:
            return True
        if state.get(n) == 2 or n not in by:
            return False
        state[n] = 1
        if any(visit(d) for d in by[n].depends):
            return True
        state[n] = 2
        return False

    return any(visit(n) for n in by)


def _milestones(p: Prompt) -> list[str]:
    out: list[str] = []
    if p.built not in LEVELS or p.tested not in LEVELS:
        return [f"{p.name}: built and tested are —, partly or yes"]
    if p.released != "—" and not re.fullmatch(r"\d+\.\d+\.\d+", p.released):
        return [f"{p.name}: released is — or a version like 0.1.0"]
    if LEVELS[p.tested] > LEVELS[p.built]:
        out.append(f"{p.name}: tested is ahead of built")
    if p.released != "—" and (p.built, p.tested) != ("yes", "yes"):
        out.append(f"{p.name}: released needs built and tested yes")
    if p.status in ("Written", "Open", "Proposed") and (p.built, p.tested) != ("—", "—"):
        out.append(f"{p.name}: {p.status} but built or tested is set")
    if p.status == "Built" and (p.built, p.tested) != ("yes", "yes"):
        out.append(f"{p.name}: Built needs built and tested yes")
    if p.status == "Partly built" and p.built != "partly":
        out.append(f"{p.name}: Partly built needs built partly")
    return out


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[2]
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "sync":
        print(f"updated {sync(root)} file(s)")
        return 0
    found = problems(root)
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
