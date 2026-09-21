# Testing

pytest. `tests/` mirrors the `src/` layout.

| Directory | Covers | Style |
| --- | --- | --- |
| `tests/unit/` | `core/`, `application/` | No I/O, no database, no network. Fast. |
| `tests/integration/` | `infrastructure/` adapters | Real database or a container; verifies the adapter honors its interface. |
| `tests/e2e/` | top-level `interfaces/` | Through the delivery surface, whichever it is — HTTP, gRPC, CLI, or a worker consuming a message. |
| `tests/fixtures/` | Shared factories and fixtures | Not tests. |

Write the test before or alongside the code, not after the fact as a coverage exercise.

## Coverage

`core/` and `application/` must stay at or above 90%. CI reports the number and fails below the threshold. Coverage elsewhere is measured but not gated, because integration coverage is a poor proxy for correctness.

Do not chase the number with tests that assert nothing.

## Mocking

Mock at boundaries only: repositories, external API clients, message publishers, the clock. Since `application/` depends on `core/interfaces/`, a fake implementation of the interface is usually better than a `Mock`, and it fails loudly when the interface changes.

That loud failure comes from `abc`, not from the typechecker: a fake inheriting the repository ABC is rejected at instantiation the moment the contract grows a method, and that happens inside pytest, which is gated. The gate deliberately does not typecheck doubles — `mypy --strict src` excludes `tests/` — so run `mypy --strict src tests` locally when you change a contract; the `tests.*` override in `pyproject.toml` is what keeps that run readable rather than a wall of `no-untyped-def`. It catches strictly more than the ABC does. An ABC rejects a fake that is *missing* a method, but a fake whose method has drifted out of arity is still instantiable, so pytest stays green until something calls it down the wrong path. Where the contract is a `Protocol` rather than an ABC, subclassing enforces nothing, because a protocol member with a `...` body is not an abstract method; have the fake inherit an ABC instead, or lean on that wider mypy run.

Bind a fake to its own name when the test asserts on it. Reached through the contract, `uow.repo` narrows to the declared type, so a fake-only attribute is not there: build `repo = FakeThingRepository()`, pass it to the Unit of Work, and assert on `repo`.

Never mock the code under test or the domain logic it calls. A test that mocks a domain service is asserting that you wrote the mock correctly.

## Fixtures and property tests

Use factories for entity construction so a new required field is a one-line change. Reach for Hypothesis on pure functions with interesting input spaces — parsers, money arithmetic, date handling — not on everything.
