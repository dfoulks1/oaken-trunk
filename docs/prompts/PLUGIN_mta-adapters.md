# MTA adapters: `steamer qmail submit` and `steamer postfix submit`

**Read first:** `docs/prompts/CONTEXT.md`, `docs/prompts/context/PLUGIN.md`, `docs/plugins.md`.
**Depends on:** [CORE_plugin-host](CORE_plugin-host.md), [CLI_client](CLI_client.md), [CORE_operation-registry](CORE_operation-registry.md).
**Lift:** S
**Delivers:** First-party qmail and Postfix commands that wrap `submit` with each MTA's conventions
**Track:** `PLUGIN_`. Package `oaken_trunk_mta`, shipped in the core wheel. Core changes: none (`BaseMTA` is built in CORE_plugin-host).

## Goal

Hand mail to Trunk the way each MTA expects, so the MTA's quirks stay out of core and another MTA is one more
small plugin.

## Decided

- Two `BaseMTA` subclasses, `qmail` and `postfix`, in the group `oaken_trunk.mtas`. Each is class attributes
  only. The base supplies `submit`, which calls core `submit` and nothing else. It only maps the MTA's conventions.
- The conventions are data in the command's `cli` metadata: env defaults and the exit map. No client code.
- qmail: `SENDER` and `RECIPIENT` from the environment. Exit 0 accepted, 111 temporary, 100 permanent.
- Postfix: sender and recipient from arguments (`${sender}` `${recipient}`). Exit as sysexits.
- Another MTA is a third-party plugin of the same shape.

## Not in scope

Delivery or queue handling. The LMTP target (PLUGIN_lmtp-ingest). The guides (DOCS_mta-guides).

## Requirements

1. **`qmail`.** `sender_env = "SENDER"`, `recipient_env = "RECIPIENT"`, `exit = {ok: 0, temporary: 111,
   permanent: 100}`. The message is on stdin.
2. **`postfix`.** Sender and recipient as arguments, `exit` as sysexits (0, 75, 65).
3. **Contract.** Each runs `MTAContract`.
4. **Docs.** `plugins.md` example, `api-and-cli.md`, softmap, status table.

## Acceptance criteria

- With the daemon down, `steamer qmail submit` exits 111 and `steamer postfix submit` exits 75. A refused
  recipient exits 100 and 65. An accepted message exits 0 for both.
- The qmail command reads `SENDER` and `RECIPIENT` when the flags are absent.
- A `BaseMTA` subclass cannot call any operation but `submit`. Standard checks pass.

## Open questions (defaults in bold)

1. Do both ship in the core wheel? **Yes. They are tiny.**

## Report-back checkpoint

End with the report from `CONTEXT.md`, naming the open questions that took the default. Then stop.
