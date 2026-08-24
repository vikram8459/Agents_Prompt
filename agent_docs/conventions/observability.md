# Configuration, logging, errors, observability

## Configuration

12-factor: all configuration comes from the environment, read through `pydantic-settings` in `config/settings.py`. Settings are validated once at startup and injected; modules do not call `os.getenv` themselves.

Every variable is documented in `.env.example` with a safe placeholder value. Adding a setting means updating that file in the same change.

## Logging

Structured JSON via `structlog`, never `print`. Every log line carries a correlation ID bound at the entry point and propagated through the request, so a single request can be reconstructed across services.

Log at the boundary where you have context. Do not log and re-raise the same error at three levels; the top-level handler will log it once with the full traceback.

Never log secrets, tokens, or PII. See [security](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/security.md).

## Error handling

Centralized exception handlers at the interface layer map exceptions to responses:

| Source | Response |
| --- | --- |
| Domain exception from `core/exceptions.py` | Mapped 4xx with a stable machine-readable error code |
| Validation error | 422 with field-level detail |
| Anything unhandled | 500 with a correlation ID and no internal detail |

Client-facing messages never include stack traces, SQL, or internal paths. The correlation ID is what connects the user's report to the log entry.

Never catch an exception and continue silently.

## Metrics and tracing

- Prometheus metrics for request rate, error rate, and latency, plus domain counters that matter to the business.
- OpenTelemetry tracing with context propagated across service calls.
- `/health` for liveness (is the process up) and `/ready` for readiness (are dependencies reachable). Keep them distinct: a failing readiness check should drain traffic, a failing liveness check should restart the pod.
