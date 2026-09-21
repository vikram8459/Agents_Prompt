# Configuration, logging, errors, observability

## Configuration

12-factor: all configuration comes from the environment, read through `pydantic-settings` in `config/settings.py`. Settings are validated once at startup and injected; modules do not call `os.getenv` themselves.

Every variable is documented in `.env.example` with a safe placeholder value. Adding a setting means updating that file in the same change.

## Logging

Structured JSON via `structlog`, never `print`. Every log line carries a correlation ID bound at the entry point and propagated through the request, so a single request can be reconstructed across services.

Log at the boundary where you have context. Do not log and re-raise the same error at three levels; the top-level handler will log it once with the full traceback.

Never log secrets, tokens, or PII. See [security](security.md).

## Error handling

Centralized exception handlers at the interface layer map exceptions to responses. The stable machine-readable error code is transport-independent and is what clients branch on; the status below is only that transport's rendering of it.

| Condition | Base | HTTP | gRPC |
| --- | --- | --- | --- |
| The request cannot be satisfied as asked | `DomainError` | 400, 404, or 409 with the error code — see the rule below | `INVALID_ARGUMENT`, `NOT_FOUND`, or `FAILED_PRECONDITION` — same rule |
| A dependency is briefly unavailable | `TransientError` | 503 with `Retry-After` | `UNAVAILABLE` |
| Malformed or out-of-range input | Rejected at the edge, before the domain | 422 with field-level detail | `INVALID_ARGUMENT` with field-level detail |
| Missing or invalid credential | `DomainError` | 401 | `UNAUTHENTICATED` |
| Valid identity, insufficient permission | `DomainError` | 403 | `PERMISSION_DENIED` |
| Caller exhausted our quota or rate limit | `DomainError`, not `TransientError` | 429 with `Retry-After` | `RESOURCE_EXHAUSTED` |
| We exhausted a provider's quota — an upstream 429 | `TransientError` | 503 with `Retry-After` | `UNAVAILABLE` |
| Idempotency key replayed with a different payload | `DomainError` | 409 | `ALREADY_EXISTS` |
| Anything unhandled | Neither — it escaped | 500 with a correlation ID and no internal detail | `INTERNAL`, the same |

Within the first row: a malformed or out-of-range caller value is `INVALID_ARGUMENT`, a well-formed reference to something absent is `NOT_FOUND`, and a valid request that the entity's current state forbids is `FAILED_PRECONDITION`. HTTP renders those three as 400, 404, and 409 — unless a more specific 4xx exists for the condition, as 402 does for a card decline. The error code is the contract and the status is a hint, which is also what distinguishes this 409 from the idempotency-conflict 409 above.

Whose quota it is decides the base, and the two go opposite ways. A caller hitting our limit is a `DomainError` even though the identical request succeeds once the window resets, because the status has to tell them the limit is theirs rather than announce an outage of ours. Us hitting a provider's limit is a `TransientError`: the caller did nothing wrong, and passing their 429 through as ours tells them to slow down about a ceiling they cannot see. Name the two separately — `RateLimitExceededError` for ours, `ProviderRateLimitedError` for theirs — because a single name invites a handler to catch one believing it is the other, and on a queue consumer that misclassification dead-letters a message that would have succeeded on the next attempt.

Where one base maps to several statuses, register the specific handler before the general one: a handler for `RateLimitExceededError` must precede the handler for `DomainError`, or the 429 renders as a generic 4xx. Assert the specific status in a test, because registration order is the kind of thing a later refactor breaks silently. Register on fully-qualified exception types: a vendor SDK exception sharing a name with a framework exception — `ValidationError` is the common collision — will otherwise be mapped as the wrong category, reporting our bug as the caller's.

On a delivery surface with no status concept, such as a queue consumer, the same distinction decides disposition. A `DomainError` or a validation error is permanent and goes straight to the dead-letter queue, because it will fail identically on redelivery. A `TransientError` is released for redelivery with backoff and reaches the dead-letter queue only once the attempt limit is exhausted. An unhandled exception is treated as transient, since you do not yet know which it was.

Client-facing messages never include stack traces, SQL, or internal paths. The correlation ID is what connects the user's report to the log entry.

Never catch an exception and continue silently.

## Metrics and tracing

- Prometheus metrics for request rate, error rate, and latency, plus domain counters that matter to the business.
- OpenTelemetry tracing with context propagated across service calls.
- Liveness (is the process up) and readiness (are dependencies reachable) stay distinct, whatever the transport: a failing readiness check should drain traffic, a failing liveness check should restart the pod. The mechanism follows the surface — `/health` and `/ready` over HTTP, the standard `grpc.health.v1` service for gRPC, a heartbeat for a worker.
