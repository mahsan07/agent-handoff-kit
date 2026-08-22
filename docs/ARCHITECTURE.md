# Architecture

## Design summary

The kit is a protocol layer rather than a full orchestrator. A handoff can live in files, a database, or an external work tracker while retaining the same schema.

## Main components

- Create a handoff
- Attach scope and artifacts
- Record decisions and assumptions
- Transfer ownership
- Verify completion or return with a failure reason

## Initial implementation boundary

Start with a local, inspectable implementation. Prefer plain files, small typed schemas, and deterministic commands before introducing a database, hosted service, or provider-specific adapter.

## Verification

Every MVP feature should have at least one fixture, one failure case, and one visible verification artifact. Keep inferred behavior separate from measured behavior.
