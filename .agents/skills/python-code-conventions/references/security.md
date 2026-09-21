# Security

## Secrets

From the environment or a vault, never in source, never in a committed `.env`, never in a log line or an error response. `.env.example` holds placeholder values only.

If a secret reaches a commit, rotate it. Removing it from the diff is not sufficient.

## Input and output

Validate at the boundary with pydantic, so unvalidated data never reaches `application/`. Validation means asserting the shape and range you actually require, not just the type.

Use parameterized queries; never build SQL by string interpolation. Escape or encode on output according to the sink (HTML, shell, SQL, log).

## PII

- Collect only what the feature requires, and delete it when the retention period expires.
- Encrypt in transit (TLS) and at rest.
- Access is authorized per request, not per service.
- Record access to PII in an audit log, and keep PII out of ordinary application logs, traces, and error payloads.

## Dependencies

Keep dependencies current and let vulnerability and supply-chain scans run in CI. Review what a new dependency pulls in before adding it.
