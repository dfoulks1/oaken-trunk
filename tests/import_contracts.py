# SPDX-License-Identifier: Apache-2.0
"""A custom import-linter contract that matches module names by glob.

Plugins are separate top-level packages named ``oaken_trunk_<name>``. import-linter's built-in
contracts need each module named up front and cannot forbid a package by prefix, or forbid a
subpackage of their own source; this contract can.
"""

from __future__ import annotations

from fnmatch import fnmatchcase
from typing import cast

from grimp import ImportGraph
from importlinter import Contract, ContractCheck, fields, output


def _any(name: str, globs: list[str]) -> bool:
    return any(fnmatchcase(name, g) for g in globs)


class GlobForbiddenContract(Contract):
    """No module matching ``importers`` (and not ``allowed``) directly imports one matching
    ``forbidden``. With ``distinct_top_level``, imports within one top-level package are fine."""

    type_name = "glob_forbidden"

    importers = fields.ListField(subfield=fields.StringField())
    forbidden = fields.ListField(subfield=fields.StringField())
    allowed = fields.ListField(subfield=fields.StringField(), required=False, default=[])
    distinct_top_level = fields.BooleanField(required=False, default=False)

    def check(self, graph: ImportGraph, verbose: bool) -> ContractCheck:
        importers = cast(list[str], self.importers)
        forbidden = cast(list[str], self.forbidden)
        allowed = cast(list[str], self.allowed)
        distinct = cast(bool, self.distinct_top_level)
        broken: list[str] = []
        for importer in sorted(graph.modules):
            if not _any(importer, importers) or _any(importer, allowed):
                continue
            for imported in sorted(graph.find_modules_directly_imported_by(importer)):
                if not _any(imported, forbidden):
                    continue
                if distinct and imported.split(".")[0] == importer.split(".")[0]:
                    continue
                for d in graph.get_import_details(importer=importer, imported=imported):
                    broken.append(f"{importer} -> {imported} (l.{d['line_number']})")
        return ContractCheck(kept=not broken, metadata={"broken": broken})

    def render_broken_contract(self, check: ContractCheck) -> None:
        for line in check.metadata["broken"]:
            output.print_error(line, bold=False)
