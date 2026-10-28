# SPDX-License-Identifier: Apache-2.0
import os
import re
import sys
from pathlib import Path

import pytest

from oaken_trunk.envelope import is_local, normalise_address
from oaken_trunk.errors import CODES, Condition, TrunkError
from oaken_trunk.ids import delivery_id, new_id
from oaken_trunk.paths import PathError, ensure_dir, resolve_paths


def test_home_gives_three_dirs(tmp_path: Path) -> None:
    p = resolve_paths({"OAKEN_TRUNK_HOME": str(tmp_path)})
    assert (p.config, p.data, p.run) == (tmp_path / "config", tmp_path / "data", tmp_path / "run")
    assert p.config_file == tmp_path / "config" / "config.toml"
    p.ensure()
    assert all(d.is_dir() for d in (p.config, p.data, p.run))


@pytest.mark.skipif(not sys.platform.startswith("linux"), reason="the system layout is Linux's")
def test_linux_layout_when_home_unset() -> None:
    p = resolve_paths({})
    assert (str(p.config), str(p.data), str(p.run)) == (
        "/etc/oaken-trunk",
        "/var/lib/oaken-trunk",
        "/run/oaken-trunk",
    )


@pytest.mark.skipif(os.name != "posix", reason="Windows has no POSIX mode bits")
def test_dirs_are_owner_only_and_world_writable_refused(tmp_path: Path) -> None:
    assert ensure_dir(tmp_path / "new").stat().st_mode & 0o077 == 0
    open_dir = tmp_path / "open"
    open_dir.mkdir()
    open_dir.chmod(0o777)
    with pytest.raises(PathError, match="world-writable"):
        ensure_dir(open_dir)


@pytest.mark.parametrize(
    ("raw", "normal"),
    [
        ("Bob@Example.ORG", "Bob@example.org"),
        ("bob+Tag@EXAMPLE.org", "bob+Tag@example.org"),
        ('"a@b"@Example.org', '"a@b"@example.org'),
    ],
)
def test_address_normalises(raw: str, normal: str) -> None:
    assert normalise_address(raw) == normal


@pytest.mark.parametrize("bad", ["bob", "@example.org", "bob@"])
def test_malformed_address(bad: str) -> None:
    with pytest.raises(TrunkError) as e:
        normalise_address(bad)
    assert e.value.condition is Condition.MALFORMED


def test_is_local() -> None:
    assert is_local("bob@Example.org", ["example.org"])
    assert not is_local("bob@example.net", ["example.org"])


def test_ids_unique_sorted_and_shaped() -> None:
    ids = [new_id() for _ in range(10_000)]
    assert len(set(ids)) == len(ids)
    assert sorted(ids) == ids
    assert all(re.fullmatch(r"[0-9A-HJKMNP-TV-Z]{26}", i) for i in ids)
    assert delivery_id(ids[0], 1) == f"{ids[0]}-1"


@pytest.mark.parametrize("condition", list(Condition))
def test_every_error_has_three_codes(condition: Condition) -> None:
    smtp, http, exit_code = CODES[condition]
    assert re.fullmatch(r"([45])\d\d \1\.\d{1,3}\.\d{1,3}", smtp)
    assert 400 <= http < 600
    # A temporary SMTP reply is a temporary exit, and only then.
    assert (exit_code == 75) == smtp.startswith("4")
    assert exit_code in {65, 67, 75, 77}


def test_named_codes() -> None:
    assert TrunkError(Condition.SPOOL_FULL).codes == ("452 4.3.1", 507, 75)
    assert TrunkError(Condition.REFUSED_RECIPIENT).codes[::2] == ("550 5.1.1", 67)
