# 6. Plugins extend standard base classes

- Status: accepted
- Date: 2026-10-24

**Context.** Trunk must be extensible around a solid core, and the plugin model should feel like
Oaken Mail's so contributors need to learn it once.

**Decision.** Every kind extends a common `BasePlugin` (context, lifecycle, health, `@command`, declared operation calls); a plugin that fits no kind extends it directly. Each plugin kind (ingestor, spool, sender, authenticator, listener) has a base class in `oaken_trunk.plugins.base`
that provides the context, lifecycle, health, lenient return coercion and capability inference from the
methods a plugin overrides. Plugins register through entry points in `oaken_trunk.*` groups, and each
kind has a contract test suite in `oaken_trunk.testing.contracts` that first-party and third-party
plugins both run. A method marked `@command` becomes a registry operation; unmarked methods are unreachable. Plugins are in-process, trusted and unsandboxed in v1. The contracts are stable surface
(versioned as in Oaken Mail's ADR 0010) because third-party plugins and consumers depend on them.

**Consequences.** A contract change needs a snapshot update and an ADR. The base classes enforce the
streaming and memory rule, so a buffering plugin fails the suite rather than the gateway.
