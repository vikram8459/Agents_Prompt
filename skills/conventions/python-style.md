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
        InsufficientFunds: If `source` cannot cover `amount`.
        CurrencyMismatch: If currencies differ.
    """
```

Document the `Raises:` section for every exception a caller is expected to handle. That is the part callers cannot infer from the signature.

## Control flow

- Guard clauses over nested conditionals. Return early on the invalid case.
- No bare `except:` and no bare `except Exception:` that swallows. Catch the specific exception, and either handle it or re-raise with context via `raise ... from err`.
- Raise domain exceptions from `core/exceptions.py` inside `core/` and `application/`. Infrastructure exceptions (`sqlalchemy.exc`, `httpx`) are translated at the adapter boundary and never propagate inward.
