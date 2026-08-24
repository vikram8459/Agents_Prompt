# API design

## HTTP

FastAPI, with routers in `interfaces/api/`. Pydantic models define request and response schemas and validate at the edge, so nothing unvalidated reaches `application/`.

Request and response models belong to the delivery layer. Do not reuse a domain entity as a response model; that couples your public contract to internal structure and leaks fields you did not mean to publish. Map explicitly.

Routers stay thin: parse, call one use case, map the result. Business logic in a route handler belongs in `application/`.

## Conventions

- Pagination on every collection endpoint, with a consistent parameter shape across the API. Never return an unbounded list.
- Filtering and sorting via query parameters, with an explicit allowlist of sortable fields.
- OpenAPI is generated from the pydantic models, so keep field descriptions and examples on the models themselves.

## Idempotency

Every mutating endpoint that a client could retry accepts an idempotency key and returns the original result on replay. Clients retry on timeout, and a timeout does not tell them whether the write landed.

## gRPC

For high-throughput internal RPC. `.proto` files are versioned and published alongside the service; generated stubs are not hand-edited. Additive field changes only within a major version.

## Errors

Error handling is centralized in exception handlers at the interface layer, not repeated per route. See [observability](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/observability.md).
