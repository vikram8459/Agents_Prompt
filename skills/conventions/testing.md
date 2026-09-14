# Testing

pytest. `tests/` mirrors the `src/` layout.

| Directory | Covers | Style |
| --- | --- | --- |
| `tests/unit/` | `core/`, `application/` | No I/O, no database, no network. Fast. |
| `tests/integration/` | `infrastructure/` adapters | Real database or a container; verifies the adapter honors its interface. |
| `tests/e2e/` | `interfaces/` | Through the HTTP or CLI surface. |
| `tests/fixtures/` | Shared factories and fixtures | Not tests. |

Write the test before or alongside the code, not after the fact as a coverage exercise.

## Coverage

`core/` and `application/` must stay at or above 90%. CI reports the number and fails below the threshold. Coverage elsewhere is measured but not gated, because integration coverage is a poor proxy for correctness.

Do not chase the number with tests that assert nothing.

## Mocking

Mock at boundaries only: repositories, external API clients, message publishers, the clock. Since `application/` depends on `core/interfaces/`, a fake implementation of the interface is usually better than a `Mock`, and it fails loudly when the interface changes.

Never mock the code under test or the domain logic it calls. A test that mocks a domain service is asserting that you wrote the mock correctly.

## Fixtures and property tests

Use factories for entity construction so a new required field is a one-line change. Reach for Hypothesis on pure functions with interesting input spaces — parsers, money arithmetic, date handling — not on everything.
