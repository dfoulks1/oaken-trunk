# SPDX-License-Identifier: Apache-2.0
"""Settings: defaults < ``config.toml`` < ``OAKEN_TRUNK_*``. Strict: an unknown key is an error.

Nested keys in the environment use ``__``: ``OAKEN_TRUNK_WORKERS__COUNT=1``. Plugin tables
(``[ingest.<name>]``, ``[store.<name>]``) pass through here; the plugin host validates them.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ByteSize,
    ConfigDict,
    Field,
    JsonValue,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

_MS = {"ms": 1, "s": 1000, "m": 60_000, "h": 3_600_000, "d": 86_400_000}
_DURATION = re.compile(r"(\d+)\s*(ms|s|m|h|d)")
_SECRET_WORDS = {"password", "token", "secret"}


class SettingsError(Exception):
    pass


def _in_unit(unit_ms: int) -> Callable[[object], object]:
    """Accept a duration string (``"5m"``) for a key named in one unit (``lease_seconds``)."""

    def parse(value: object) -> object:
        if isinstance(value, str) and (m := _DURATION.fullmatch(value.strip())):
            ms = int(m[1]) * _MS[m[2]]
            if ms % unit_ms:
                raise ValueError(f"{value!r} is not a whole number of this key's unit")
            return ms // unit_ms
        return value

    return parse


Millis = Annotated[int, BeforeValidator(_in_unit(1)), Field(ge=0)]
Seconds = Annotated[int, BeforeValidator(_in_unit(1000)), Field(ge=0)]
Days = Annotated[int, BeforeValidator(_in_unit(86_400_000)), Field(ge=0)]
Positive = Annotated[int, Field(ge=1)]
Domain = Annotated[str, AfterValidator(str.lower)]
PluginTables = dict[str, dict[str, JsonValue]]


class _Section(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Workers(_Section):
    count: Positive = 1
    thread_count: Positive = 1
    max_count: Positive = 8
    max_threads: Positive = 32

    @field_validator("count")
    @classmethod
    def _one_worker(cls, v: int) -> int:
        if v > 1:
            raise ValueError("more than one worker needs the supervisor, not built yet; use 1")
        return v

    @field_validator("thread_count")
    @classmethod
    def _one_thread(cls, v: int) -> int:
        if v > 1:
            raise ValueError("more than one I/O thread is not tested yet; use 1")
        return v


class Server(_Section):
    host: str = "127.0.0.1"
    port: int = 8080
    max_header_bytes: ByteSize = ByteSize(64 << 10)
    max_inflight: Positive = 64
    max_message_size: ByteSize = ByteSize(25 << 20)
    retry_after_seconds: Seconds = 30


class Mail(_Section):
    local_domains: list[Domain] = []


class Spool(_Section):
    max_spool_bytes: ByteSize = ByteSize(20 << 30)
    max_deliveries: Positive = 1_000_000
    max_devices: Positive = 1000
    device_expiry_days: Days = 30
    lease_seconds: Seconds = 300


class Store(BaseModel):
    """Which store serves each role, plus one ``[store.<name>]`` table per store plugin."""

    model_config = ConfigDict(extra="allow", frozen=True)
    bodies: str = "dir"
    queues: str = "dir"
    coordination: str = "dir"

    @model_validator(mode="after")
    def _plugin_tables_only(self) -> Store:
        for key, value in (self.model_extra or {}).items():
            if not isinstance(value, dict):
                raise ValueError(f"unknown key {key!r} (only a [store.<name>] table may be added)")
        return self


class Surface(_Section):
    scheme: Literal["ed25519", "apptoken", "bearer"] = "ed25519"
    keys_dir: str
    max_clock_skew_seconds: Seconds = 60


class Security(_Section):
    ingest: Surface = Surface(keys_dir="config/keys/ingest")
    consume: Surface = Surface(keys_dir="config/keys/consume")
    admin: Surface = Surface(keys_dir="config/keys/admin")
    mcp: Surface = Surface(keys_dir="config/keys/mcp")


class AdminMcp(_Section):
    enabled: bool = False
    local_only: bool = True
    tier: str = "stats"


class Admin(_Section):
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8081
    ui: bool = True
    mcp: AdminMcp = AdminMcp()


class Sign(_Section):
    enabled: bool = False
    selector: str = "trunk"
    key_file: str = "config/keys/dkim/trunk.pem"


class MailAuth(_Section):
    dkim_verify: bool = True
    spf: bool = True
    dmarc: Literal["off", "record", "enforce"] = "record"
    trusted_hops: list[str] = []
    sign: Sign = Sign()


class Log(_Section):
    level: Literal["debug", "info", "warning", "error"] = "info"
    envelope: Literal["none", "hashed"] = "none"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OAKEN_TRUNK_", env_nested_delimiter="__", extra="forbid", frozen=True
    )

    version: Literal[1] = 1
    workers: Workers = Workers()
    server: Server = Server()
    ingest: PluginTables = {}
    mail: Mail = Mail()
    spool: Spool = Spool()
    store: Store = Store()
    security: Security = Security()
    admin: Admin = Admin()
    mailauth: MailAuth = MailAuth()
    log: Log = Log()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # First wins: the environment, then the file (passed in as init values), then defaults.
        return env_settings, init_settings


def _is_secret(key: str) -> bool:
    key = key.lower()
    return "private_key" in key or not _SECRET_WORDS.isdisjoint(key.split("_"))


def _refuse_secrets(table: Mapping[str, Any], file: Path, prefix: str = "") -> None:
    for key, value in table.items():
        name = f"{prefix}{key}"
        if _is_secret(key):
            raise SettingsError(
                f"{file}: `{name}` looks like a secret, and secrets never live in config.toml. "
                "Put it in an owner-only file and name that file, or set it in the environment."
            )
        for child in value if isinstance(value, list) else [value]:
            if isinstance(child, dict):
                _refuse_secrets(child, file, f"{name}.")


def load_settings(config_file: Path) -> Settings:
    """Load and validate settings. A missing file means defaults (and the environment)."""
    try:
        data = tomllib.loads(config_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        data = {}
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as e:
        raise SettingsError(f"{config_file}: {e}") from None
    _refuse_secrets(data, config_file)
    try:
        return Settings(**data)
    except ValidationError as e:
        lines = [
            f"{'.'.join(map(str, err['loc']))}: "
            + ("unknown key" if err["type"] == "extra_forbidden" else err["msg"])
            for err in e.errors()
        ]
        raise SettingsError(
            f"invalid settings in {config_file} or OAKEN_TRUNK_* environment:\n  "
            + "\n  ".join(lines)
        ) from None
