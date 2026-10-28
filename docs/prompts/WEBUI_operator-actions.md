# Operator actions: the CLI's actions and diagnostics, in the web UI

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/WEBUI.md`, ADR 0007, `WEBUI_management-ui.md` (its status block).
**Depends on:** [WEBUI_management-ui](WEBUI_management-ui.md), [CORE_diagnostics](CORE_diagnostics.md), [CORE_enrollment](CORE_enrollment.md).
**Lift:** M
**Delivers:** Devices, diagnostics and every mutating action the CLI has, as UI pages with confirmation
**Track:** `WEBUI_`. Still a client of the registry only.

## Goal

The operator does in the browser what they can already do with `steamer`, and nothing more.

## Requirements

1. **Diagnostics pages.** `trace`, `devices`, `refusals` and `probe` (CORE_diagnostics).
2. **Actions.** Delete or release a message, issue an enrollment code, revoke a device, run `checkup`. Each
   maps to an operation with a CLI command, and a mutating one needs the same confirmation (`--yes`).
3. **Audit.** Every action is audited under the UI's principal, as the CLI's would be.
4. **Docs.** The UI page of the docs, softmap, status table.

## Acceptance criteria

- Each action has a CLI twin, checked by a test over the registry. An action without confirmation is refused.
- A token or body sentinel never reaches a page or a log. Standard checks pass.

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
