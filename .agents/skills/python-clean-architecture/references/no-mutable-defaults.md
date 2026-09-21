# No mutable defaults

A default argument is evaluated once, when the `def` executes, not on each call. Every call that omits the argument shares that one object, and a function outlives every request that passes through it, so an append in one call is visible to the next — and in a long-lived process, to a different user's request an hour later. The symptom is a collection that grows across calls nobody can explain locally, because nothing in the failing call is wrong.

Never write one.

```python
def add_tags(thing: Thing, tags: list[str] = []) -> Thing:           # one list, shared by every call
def add_tags(thing: Thing, tags: Sequence[str] = ()) -> Thing:       # immutable default, safe
def add_tags(thing: Thing, tags: Sequence[str] | None = None) -> Thing:  # when absent differs from empty
```

## Which default to pick

Prefer the empty tuple with a `Sequence` or `Mapping` annotation. It needs no unpacking in the body, and the annotation states that the function will not mutate what it was handed — which in `core/` is almost always true.

Use `None` only when absent and empty mean different things, such as a filter that is unset versus a filter that matches nothing. Resolve it on the first line of the body, and do not use `or` to do it, since that also swallows a legitimately empty argument:

```python
def search(tags: Sequence[str] | None = None) -> list[Thing]:
    """Return things matching every tag, or all things when `tags` is None."""
    if tags is None:
        return self._repo.list_all()
```

## The same bug in three other shapes

Ruff's `B006` catches the signature form and nothing below it. These are the ones that reach review:

| Shape | Why it shares | Fix |
| --- | --- | --- |
| A module-level mutable constant used as a default, such as `DEFAULT_TAGS: list[str] = []` in `config/constants.py` | One list, however many functions default to it | Constants are immutable: `tuple`, `frozenset`, or a function returning a fresh `Mapping` |
| A mutable class attribute | Shared by every instance of the class, not per object | Assign it in `__init__` |
| A mutable dataclass field | `@dataclass` rejects a list literal outright, but a shared factory or an aliased constant slips through | `field(default_factory=list)` |

The dataclass case carries an extra rule on a value object. A `frozen=True` dataclass holding a list is still mutable through that list and is not hashable, so it fails the equality-by-value contract in [OOP and contracts](oop-and-contracts.md). Store a `tuple` or a `frozenset`, and convert in `__post_init__` if the caller hands you a list.

## Calls in defaults

Bugbear's `B008` flags any call used as a default, which catches the related `timestamp: datetime = datetime.now()` bug — one timestamp frozen at import time — and also FastAPI's `Depends(...)`, where the call in the default is the intended idiom. A router that needs it adds the symbol to `extend-immutable-calls` under `[tool.ruff.lint.flake8-bugbear]` in `pyproject.toml`, rather than scattering `# noqa: B008` down the file.

An injected clock is the domain-side answer to `datetime.now()`: `core/` takes a clock through the constructor like any other collaborator, so tests control time instead of patching it.
