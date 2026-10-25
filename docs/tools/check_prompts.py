# SPDX-License-Identifier: Apache-2.0
"""The prompt series stays consistent. The rules are in ``prompts.py`` (the manifest tool);
``check_docs.check`` runs this through its extension hook, like ``check_commands``."""

import prompts
from model import Config


def check(cfg: Config) -> list[str]:
    return prompts.problems(cfg.repo_root)
