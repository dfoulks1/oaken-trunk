# The Oaken family: where Trunk sits

Read with [CONTEXT.md](../CONTEXT.md). This is the map, so a contributor knows
what Trunk is and, more useful, what it is not. Trunk is the one piece built;
the rest are planned and named, not code on disk.

## The metaphor

Oak is the raw material: the intelligence, the indices, the data. The tools
(Steamer, Basket, Handle, Bureau) are the craft that shapes it. Every name is a
physical object. A name that needs a footnote is the wrong one.

## The map

```
 SERVER   external mail -> oaken-trunk (steamer): stateless gateway, spool
                                 | client pulls over POP3; trunk does not push
 CLIENT   oaken-mail (oaken):     AI engine + vector index
          oaken-grove (basket):   CRM relationship graph
          oaken-seasons (handle): smart calendar
          Bureau:                 localhost desk UI over the three above
```

| Component     | CLI       | Does                                      |
|---------------|-----------|-------------------------------------------|
| oaken-trunk   | `steamer` | Stateless mail spool, transport           |
| oaken-mail    | `oaken`   | Vector index, semantic search, AI context |
| oaken-grove   | `basket`  | Contact dossiers, relationships           |
| oaken-seasons | `handle`  | Schedules, holds, availability            |
| Bureau        | desk UI   | Unites mail, CRM, calendar                |

## The two boundaries that bind this repo

- **Trunk knows nothing of its consumers.** The client reaches into the spool
  and pulls, over POP3 through a retriever plugin; a message is gone once every
  device has it (ADR 0013). Trunk never imports oaken-mail (ADR 0002). The reach
  lives in a plugin in the *client's* repo, never here.
- **Bureau never touches Trunk or steamer.** Server transport and client
  intelligence stay on opposite sides of that line.

The rest of the family is context. In this repo, build Trunk as if the
consumers are strangers, because to Trunk they are.
