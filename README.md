# Oaken Trunk

Oaken Trunk is a small, stateless mail gateway with a durable spool: the gateway processes hold no state, the spool does. It receives mail over SMTP, LMTP, HTTP or a pipe,
streams each message into a spool, and tells consumers it is there. Consumers lease a message,
do their work, and acknowledge it. Trunk keeps no mailbox, no index and no IMAP: it replaces the
*delivery* step into a local mailbox (the Dovecot LDA role), not mailbox access.

**Status: pre-alpha. This repository holds the design and the build prompts; there is no code yet.**
See the [roadmap](ROADMAP.md).

- License: [Apache-2.0](LICENSE)
- Companion project: [Oaken Mail](https://github.com/dfoulks1/oaken-mail), which consumes a trunk
  through a provider plugin that lives in *its* repository. Trunk does not depend on Oaken Mail and is
  meant to be useful without it.

## How it fits together

```
 Postfix / qmail (LMTP, pipe)   SMTP 25/587   HTTP /v1/send   CLI (stdin)      <- ingestors (plugins)
                      \             |              |             /
                       +------------+--- core -----+------------+
                         authenticate, size and rate limits, stream to spool
                                      |
                       spool (plugin): directory (default), Redis, S3 + SQS
                                      |
                  notify  ->  consumers: lease -> process -> ack | nack
                                      |
                         senders (plugin): outbound relay, later
```

Every capability is one registered operation. The HTTP API and the CLI are generated from the same
registry, so every endpoint has a command. See [architecture](docs/architecture/overview.md).

## Design rules

- **Never hold a message in memory.** Bodies stream from the socket to the spool in fixed chunks. Where the spool keeps them (disk, Redis, S3) is the spool plugin's business.
- **Bounded, not buffered.** `max_inflight` and `max_message_size` apply at the door. Over a limit the
  sender gets a retryable 4xx (SMTP 451, HTTP 503 with `Retry-After`) and the queue backs up on the
  sender's side, not in our RAM.
- **Accepted means durable.** The default spool fsyncs before the SMTP 250; `batched` shares one fsync
  across concurrent messages. `durability = "volatile"` is an explicit opt-in.
- **At-least-once delivery.** Leases expire, messages come back, consumers dedupe on message id.
- **Scale with processes.** Workers share nothing but the spool.
- **Light enough to sit beside Postfix or qmail**, not replace them.

## Configuration and data

Same home system as Oaken Mail, with its own variable. `OAKEN_TRUNK_HOME` relocates everything
(`<dir>/config/config.toml`, `<dir>/data`). Without it, platform folders are used
(`~/.config/oaken-trunk/config.toml` on Linux). Precedence: defaults < `config.toml` <
`OAKEN_TRUNK_*` environment variables. Secrets never go in `config.toml`.
See [`config.example.toml`](config.example.toml).
