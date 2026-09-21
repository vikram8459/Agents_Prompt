# Concurrency, performance, caching

Measure before optimizing. Profile the actual workload; do not restructure code around a guess about where time goes.

## Concurrency

- asyncio for I/O-bound work. One blocking call inside a coroutine stalls the entire event loop, so a synchronous driver, `requests`, or `time.sleep` in async code is a defect. Use `asyncio.to_thread` when no async equivalent exists.
- `httpx` is the default outbound HTTP client, async anywhere on a request path. `requests` is acceptable only in a genuinely synchronous context — a CLI command or a worker task — and then needs `types-requests` in the dev group to pass `mypy --strict`. Either way the client is an adapter and follows the placement rule in the `python-clean-architecture` skill.
- Thread pools for blocking I/O you cannot make async; process pools for CPU-bound work, since the GIL means threads will not help.
- Anything long-running or retryable goes to a background worker (Celery, RQ, APScheduler) rather than a request handler. A user should not wait on a job. The broker adapter belongs in `infrastructure/messaging/`, the work itself in `application/use_cases/`, and the worker entry point in top-level `interfaces/` — it is a delivery surface like a router, and stays as thin as one.

## Caching

Layer deliberately: `functools.lru_cache` sits directly on the pure function it memoizes, while Redis serves anything shared across processes or instances, behind a contract in `core/interfaces/` with the adapter in `infrastructure/cache/`.

Every cache entry needs a defined invalidation rule and a TTL before it is added. A cache without an invalidation story is a source of stale-data bugs, and "we'll add invalidation later" means serving stale data in production.

Never cache per-user data under a key that is not scoped to the user.
