---
name: python-code-conventions
description: Write Python that conforms to this project's typing, docstring, testing, persistence, API, observability, security, and performance conventions. Covers mypy strict annotations, Google docstrings, exception naming and translation, pytest layout and coverage gates, repositories and Unit of Work, Alembic migrations, FastAPI routers with pydantic validation, cursor pagination, idempotency keys, structlog and correlation IDs, error-to-response mapping, secrets and PII handling, asyncio, httpx, and caching. Use when writing or reviewing any Python module, test, endpoint, repository, migration, log line, cache, or background task.
compatibility: Python 3.12 project managed with Poetry, linted by ruff with the D and ANN rule sets, typechecked by mypy strict, tested with pytest.
---

# Python code conventions

Ruff already enforces PEP 8, import order, and formatting, so none of that is a judgment call. What follows are the decisions the tools cannot make, plus the rules that carry a reason worth knowing.

## Applies to every module

- Every signature is annotated, including `-> None`. `mypy --strict` passes. A `# type: ignore` needs a trailing comment explaining why, and never silences a real error.
- Avoid `Any`. Narrow untyped boundary values immediately with a `TypedDict`, a pydantic model, or a cast plus validation.
- Google-style docstrings on every module, public class, and public method, with a `Raises:` section for every exception a caller is expected to handle. That is the part callers cannot infer from the signature.
- Guard clauses over nested conditionals. Return early on the invalid case.
- No bare `except`, and no `except Exception` that swallows. Catch the specific exception, then handle it or re-raise with context via `raise ... from err`.
- Domain exception names end in `Error`, because ruff's `N818` requires it. Raise them from `core/exceptions.py` inside `core/` and `application/`; translate infrastructure exceptions at the adapter boundary so they never propagate inward.
- Every exception that describes a condition we anticipated inherits from one of two bases in `core/exceptions.py`: `DomainError` when retrying unchanged cannot help, `TransientError` when the same request may succeed later. The delivery layer maps on that distinction, so getting it wrong reports our outage as the caller's mistake. An exception marking one of our own defects inherits from neither, is mapped by nothing, and renders as a 500.

See [python style](references/python-style.md) for the docstring example and the full typing rules.

## Pick the reference for the task

| Task | Reference |
| --- | --- |
| Writing tests, choosing a test directory, deciding what to mock | [testing](references/testing.md) |
| Repositories, Unit of Work, SQLAlchemy, Alembic migrations | [persistence](references/persistence.md) |
| HTTP or gRPC endpoints, pagination, idempotency, schemas | [api design](references/api-design.md) |
| Settings, logging, error mapping, metrics, tracing, health checks | [observability](references/observability.md) |
| Secrets, PII, input validation, dependency risk | [security](references/security.md) |
| asyncio, outbound HTTP, background workers, caching | [performance](references/performance.md) |

## Rules most often got wrong

- **Validate at the edge.** Pydantic models at the interface layer assert the shape *and range* you require, so unvalidated data never reaches `application/`. Never reuse a domain entity as a response model; map explicitly.
- **Mock only at boundaries** — repositories, external clients, publishers, the clock — and prefer a fake implementation of the `core/interfaces/` contract over a `Mock`, because a fake fails loudly when the interface changes. Never mock the code under test or the domain logic it calls.
- **Coverage is gated at 90% on `core/` and `application/` only.** Coverage elsewhere is measured, not gated, because integration coverage is a poor proxy for correctness. Do not chase the number with tests that assert nothing.
- **`core/` stays ORM-free.** Entities are plain classes or dataclasses, never declarative models. The mapping layer in `infrastructure/database/` is the accepted cost.
- **Never log secrets, tokens, or PII**, in log lines, traces, or error payloads. A correlation ID bound at the entry point is what connects a user's report to the log entry.
- **Every cache entry needs a TTL and a stated invalidation rule before it is added**, and per-user data is never cached under an unscoped key.
- **One blocking call stalls the whole event loop.** A synchronous driver, `requests`, or `time.sleep` inside a coroutine is a defect; `httpx` is the default outbound client.

## Related skills

- Which layer a given module belongs in, and how to define its contract: the `python-clean-architecture` skill.
- Tool configuration, the gate commands, and what each change tier must ship: the `python-workflow-and-tooling` skill.
