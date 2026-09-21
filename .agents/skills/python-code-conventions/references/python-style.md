# Python style

Ruff enforces PEP 8 and import order, so formatting is not a judgment call. What follows are the decisions ruff cannot make for you.

## Typing

- Every function signature is annotated, including `-> None`.
- `mypy --strict` must pass. Do not add `# type: ignore` without a trailing comment explaining why, and never to silence a real error.
- Avoid `Any`. If a value is genuinely untyped at a boundary, narrow it immediately with a `TypedDict`, a pydantic model, or an explicit cast plus validation.
- `from __future__ import annotations` at the top of modules using forward references.
- Prefer `@dataclass(frozen=True)` for anything that does not need to mutate.

## Docstrings

Google style, on every module, public class, and public method. Private helpers need one only when the intent is not obvious from the name.

```python
def transfer(source: Account, target: Account, amount: Money) -> Transfer:
    """Move funds between two accounts.

    Args:
        source: Account to debit. Must have sufficient available balance.
        target: Account to credit.
        amount: Positive amount to move. Currency must match both accounts.

    Returns:
        The recorded transfer.

    Raises:
        InsufficientFundsError: If `source` cannot cover `amount`.
        CurrencyMismatchError: If currencies differ.
    """
```

Document the `Raises:` section for every exception a caller is expected to handle. That is the part callers cannot infer from the signature.

## Control flow

- Guard clauses over nested conditionals. Return early on the invalid case.
- No bare `except:` and no bare `except Exception:` that swallows. Catch the specific exception, and either handle it or re-raise with context via `raise ... from err`.
- Domain exception names end in `Error` — `DuplicateThingError`, not `DuplicateThing`. Ruff's `N818` enforces it, so the suffix is not optional.
- Raise domain exceptions from `core/exceptions.py` inside `core/` and `application/`. Infrastructure exceptions (`sqlalchemy.exc`, `httpx`) are translated at the adapter boundary and never propagate inward.
- `core/exceptions.py` holds two bases, and the delivery layer maps on which one it caught:
  - `DomainError` — the request cannot be satisfied as asked, and retrying it unchanged will not help.
  - `TransientError` — the identical request may succeed later. The failing dependency need not be one we own; a provider timeout qualifies.

  Every exception that describes a condition we anticipated inherits from one of the two, whichever layer raises it — a `DuplicateThingError` translated in an adapter is still a `DomainError`. A handler that cannot tell the two apart reports our outage as the caller's mistake, and dead-letters a message that would have succeeded on the next attempt. Our own defects are the third case and inherit from neither base, which is exactly what stops a handler from matching them and renders them as the last row of the table in `observability.md`. Declare those in the module that raises them, not in `core/exceptions.py`.
- Translating a third-party client's failures: a business rejection such as a declined card is a `DomainError`, because retrying the same card gives the same answer. A timeout, connection error, or 5xx is a `TransientError`. A provider 4xx that is *not* a business rejection — bad credentials, a malformed request — is our bug rather than the caller's, so it takes the third case: catch it so the vendor class stops at the adapter boundary, re-raise our own error with `raise ... from err`, inherit from neither base, and register no handler for it, which is what renders it as a 500. A provider 429 is our quota, not the caller's, so it is a `TransientError` — raise `ProviderRateLimitedError`, kept distinct from the `RateLimitExceededError` that means a caller hit our own limit.
