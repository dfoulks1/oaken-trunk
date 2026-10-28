# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest

from oaken_trunk.settings import Settings, SettingsError, load_settings

REPO = Path(__file__).parents[3]


def _load(tmp_path: Path, text: str) -> Settings:
    f = tmp_path / "config.toml"
    f.write_text(text, encoding="utf-8")
    return load_settings(f)


def test_defaults_without_a_file(tmp_path: Path) -> None:
    s = load_settings(tmp_path / "missing.toml")
    assert s.workers.count == 1
    assert s.server.max_message_size == 25 * 1024 * 1024


def test_the_example_config_loads() -> None:
    s = load_settings(REPO / "config.example.toml")
    assert s.spool.lease_seconds == 300
    assert s.store.model_extra == {
        "dir": {
            "path": "data/store",
            "durability": "strict",
            "notify": "auto",
            "poll_interval_ms": 500,
        }
    }


def test_env_beats_file_beats_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    f = tmp_path / "config.toml"
    f.write_text("[server]\nport = 9000\nmax_inflight = 5\n", encoding="utf-8")
    monkeypatch.setenv("OAKEN_TRUNK_SERVER__PORT", "9100")
    s = load_settings(f)
    assert (s.server.port, s.server.max_inflight, s.server.host) == (9100, 5, "127.0.0.1")


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("[server]\nprot = 1\n", "server.prot: unknown key"),
        ("[admin.mcp]\nenabeld = true\n", "admin.mcp.enabeld: unknown key"),
        ("[store]\nbodeis = 'dir'\n", "unknown key 'bodeis'"),
        ("[workers]\ncount = 2\n", "more than one worker needs the supervisor"),
        ("[workers]\nthread_count = 2\n", "more than one I/O thread is not tested"),
    ],
)
def test_refused(tmp_path: Path, text: str, message: str) -> None:
    with pytest.raises(SettingsError, match=message):
        _load(tmp_path, text)


def test_unknown_env_key_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OAKEN_TRUNK_WORKERS__COUNTS", "1")
    with pytest.raises(SettingsError, match="workers.counts: unknown key"):
        load_settings(tmp_path / "missing.toml")


@pytest.mark.parametrize(
    "text",
    [
        "[ingest.smtp]\npassword = 'x'\n",
        "[store.s3]\naccess_token = 'x'\n",
        "[mailauth.sign]\nprivate_key = 'x'\n",
        "client_secret = 'x'\n",
    ],
)
def test_secret_named_key_refused(tmp_path: Path, text: str) -> None:
    with pytest.raises(SettingsError, match="looks like a secret.*file.*environment"):
        _load(tmp_path, text)


def test_sizes_and_durations_parse(tmp_path: Path) -> None:
    s = _load(
        tmp_path,
        "[server]\nmax_message_size = '10MiB'\nretry_after_seconds = '2m'\n"
        "[spool]\nmax_spool_bytes = '1GiB'\ndevice_expiry_days = '7d'\nlease_seconds = 45\n",
    )
    assert s.server.max_message_size == 10 << 20
    assert s.server.retry_after_seconds == 120
    assert s.spool.max_spool_bytes == 1 << 30
    assert (s.spool.device_expiry_days, s.spool.lease_seconds) == (7, 45)
    with pytest.raises(SettingsError, match="not a whole number"):
        _load(tmp_path, "[spool]\ndevice_expiry_days = '5h'\n")


def test_local_domains_lowercased(tmp_path: Path) -> None:
    s = _load(tmp_path, "[mail]\nlocal_domains = ['Example.ORG']\n")
    assert s.mail.local_domains == ["example.org"]
