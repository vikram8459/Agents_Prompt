# Comments

Nothing in the ruff rule set flags a stale comment, a block of commented-out code, or a TODO nobody owns. The `D` rules check that docstrings exist, not that the prose inside a function body is worth reading. So comments are the one part of a module enforced in review or not at all — and the one part that can be wrong while every gate stays green.

## The test

Before writing a comment, ask what a reader loses if it is deleted. If the answer is nothing the code already says, delete it. If the answer is a fact that lives outside the file, keep it.

## What earns one

| Carries | Example |
| --- | --- |
| Why, where the what is already clear | `# Half-up: the provider settles this way, and half-even leaves a cent unreconciled.` |
| A constraint imposed from outside | `# Provider returns 200 with an error body on a declined card, so status alone cannot be trusted.` |
| An alternative rejected at this exact line | `# Not a set: callers depend on insertion order for the receipt.` |
| A cost that looks wrong and is not | `# O(n²) is fine here: n is the supported currency list, bounded at ~30.` |
| The justification a rule demands | `# type: ignore[arg-type]  # SDK stubs type the callback as Any.` |

## What does not

- Narration of the next statement, and banner comments that label a block instead of extracting it into a named function.
- Restatements of the signature. Annotations and the docstring own the types, the arguments, and the raised exceptions.
- Change history: who edited it, when, and under which ticket. Git holds all three, and the comment is the copy that goes stale.
- Commented-out code. Delete it; version control is the undo.
- A `TODO` with no owner and no tracked issue, which is a note that will never be actioned. Write `# TODO(PROJ-123): ...` or do not write it.

```python
# Get the account
account = await self._repo.get(account_id)
# Check the balance
if account.balance < amount:
    # Raise an error
    raise InsufficientFundsError(account_id)
```

Every comment above says what the line below it says. Compare:

```python
# Authorization holds settle up to 3 days later, so the spendable figure is
# the booked balance minus holds, not the booked balance.
if account.available_balance() < amount:
    raise InsufficientFundsError(account_id)
```

## Not the same obligation as a docstring

A docstring is the contract a caller reads without opening the body; a comment is a note to whoever edits the body next. They are not interchangeable, and neither excuses the absence of the other. Keep rationale about how this implementation works out of the docstring, and keep the API contract out of comments. Google-style docstrings remain required on every module, public class, and public method — see the `python-code-conventions` skill.

Needing a comment to explain what a private helper does is a naming problem wearing a comment's clothes. Rename it, or split it until the name fits.

## By layer

- `core/` — the comment worth writing records where an invariant came from. The code states the rule; only a comment can state that the threshold is regulatory, a contract term, or a number the business picked, and that is what tells the next reader whether changing it is a refactor or a breach.
- `application/` — a use case reads as a sequence of steps, so a comment here usually marks a step that should have been a named method. The exception is ordering forced by something outside the process, such as a write that must be durable before an outbound call.
- `infrastructure/` — vendor quirks are documented here and nowhere else, at the same boundary where the vendor's types, identifiers, and exceptions stop. A comment about a provider's behavior sitting in `application/` means the leak already happened; fix the leak rather than explaining it.
- `interfaces/` (top level) — wire-compatibility notes: a field kept for an old client, a status code chosen for a consumer's retry behavior.
