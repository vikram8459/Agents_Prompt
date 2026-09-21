# API design

## HTTP

FastAPI, with routers in `interfaces/api/`. Pydantic models define request and response schemas and validate at the edge, so nothing unvalidated reaches `application/`.

Request and response models belong to the delivery layer. Do not reuse a domain entity as a response model; that couples your public contract to internal structure and leaks fields you did not mean to publish. Map explicitly.

Routers stay thin: parse, call one use case, map the result. Business logic in a route handler belongs in `application/`, and errors are mapped by centralized exception handlers at the interface layer rather than per route — `observability.md` holds the source-to-response table.

## Conventions

- Pagination on every collection endpoint, and never an unbounded list. The shape is the same API-wide: `limit` (default 50, maximum 100) plus an opaque `cursor` taken from the previous response, answered as `{"items": [...], "next_cursor": "..."}` with a null `next_cursor` on the last page.
- Keyset pagination, not `OFFSET`. Order by a total key — the sort column plus the ID as tiebreaker — and encode that key in the cursor. Under `OFFSET`, a row inserted while a client pages makes it see one row twice and miss another, and nothing in the response reveals that it happened.
- Every error response uses the same envelope, API-wide: `{"error": {"code": "...", "message": "...", "correlation_id": "..."}}`. The `code` is the stable machine-readable value clients branch on, `message` is for humans and is never parsed, and field-level validation detail goes in an optional `error.fields` map keyed by field name. `observability.md` maps each condition to a status.
- Filtering and sorting via query parameters, with an explicit allowlist of sortable fields.
- OpenAPI is generated from the pydantic models, so keep field descriptions and examples on the models themselves.

## Idempotency

Every mutating endpoint that a client could retry accepts an idempotency key and returns the original result on replay. Clients retry on timeout, and a timeout does not tell them whether the write landed.

## gRPC

For high-throughput internal RPC. `.proto` files are versioned and published from `contracts/` at the repo root; generated stubs are not hand-edited. Additive field changes only within a major version.
