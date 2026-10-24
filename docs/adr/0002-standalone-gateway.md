# 2. Trunk is a standalone gateway; Oaken Mail is one consumer

Status: accepted

**Context.** Trunk is meant to sit beside Postfix or qmail and serve any consumer, not just Oaken
Mail. Coupling it to Oaken Mail would narrow its audience and tie release cycles together.

**Decision.** Trunk never imports Oaken Mail. Consumers use a documented contract: the HTTP
lease/fetch/ack/nack API, or a spool's native form (Redis stream, SQS queue). The Oaken Mail
provider plugin (`oaken.providers`) lives in the oaken-mail repository and calls that API.

**Consequences.** Trunk needs first-party example consumers (CLI, webhook) and a stable, versioned
consumer contract. Identity parity is limited to the same home-directory convention (`OAKEN_TRUNK_HOME` here, `OAKEN_HOME` there) and standards.
