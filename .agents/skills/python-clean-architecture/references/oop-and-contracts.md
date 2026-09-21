# OOP and contracts

## Building blocks

| Concept | Rule |
| --- | --- |
| Entity | Identity plus behavior. Mutable. Equality by ID. |
| Value object | Immutable (`@dataclass(frozen=True)`). Equality by value. |
| Domain service | Stateless. Orchestrates entities and value objects. Use only when the logic belongs to no single entity. |
| Repository | Interface in `core/interfaces/`, implementation in `infrastructure/`. |
| Use case | One public entry point in `application/use_cases/`, takes a command DTO plus injected dependencies. |

Enforce invariants in constructors and at public method boundaries, so an object cannot exist in an invalid state. `frozen=True` alone does not make a value object immutable if a field holds a list or a dict — see [no mutable defaults](no-mutable-defaults.md) for that case and for the defaults and class attributes that share state between calls.

## ABC or Protocol

- `abc.ABC` with `@abstractmethod` when implementations should inherit and you want the base class to reject incomplete subclasses at instantiation.
- `typing.Protocol` for structural typing across package boundaries, and when the implementer should not have to import your package. A mutable attribute on a `Protocol` is invariant, so an implementer whose attribute holds a narrower type than the declaration is rejected by `mypy --strict`; declare shared state as a read-only `@property` when you do reach for one.

The ABC is the usual answer here. `infrastructure/` already imports `core/` to implement these contracts, so the condition for a Protocol does not arise, and only the ABC rejects an incomplete fake at instantiation — the property `testing.md` in the `python-code-conventions` skill relies on.

Keep each interface to one responsibility. A five-method interface where callers use two methods should be two interfaces.

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from myproject.core.entities.thing import Thing


class ThingRepository(ABC):
    """Persistence contract for `Thing` aggregates."""

    @abstractmethod
    async def get(self, thing_id: str) -> Thing | None:
        """Return the thing with `thing_id`, or None if absent."""

    @abstractmethod
    async def add(self, thing: Thing) -> None:
        """Persist a new thing."""

    @abstractmethod
    async def list_all(self) -> Iterable[Thing]:
        """Return all things."""


class UnitOfWork(ABC):
    """Transactional boundary around one or more repositories."""

    repo: ThingRepository

    @abstractmethod
    async def __aenter__(self) -> UnitOfWork:
        """Open the transaction."""

    @abstractmethod
    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        """Roll back on an exception, otherwise release the transaction."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit the work staged in this transaction."""

    @abstractmethod
    async def rollback(self) -> None:
        """Discard the work staged in this transaction."""
```

Every method carries a docstring, including the dunders: a `...` body does not exempt a method from the `D` rules, and neither does a `Protocol` member elsewhere.

The contracts are async because anything on a request path is: a blocking call inside a coroutine stalls the event loop. A CLI or a synchronous worker may implement the sync equivalent, but the async shape is the default. Note also that the methods speak in `Thing`, never in `object` or a dict — a contract typed loosely enough to accept anything documents nothing.

## Use case shape

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateThingCommand:
    """Input for creating a thing."""

    name: str


class CreateThing:
    """Creates a thing and persists it."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Store injected collaborators."""
        self._uow = uow

    async def execute(self, cmd: CreateThingCommand) -> Thing:
        """Create and persist a thing, returning the stored entity."""
        thing = Thing(thing_id=new_thing_id(), name=cmd.name)
        async with self._uow:
            await self._uow.repo.add(thing)
            await self._uow.commit()
        return thing
```

A class, not a module-level function: collaborators arrive through the constructor, and the single public entry point takes only the command. A use case handed its Unit of Work per call is a service locator wearing a different hat.

## Composition over inheritance

Inherit only for genuine subtype relationships that satisfy Liskov substitution: any caller holding the base type must work with the subtype without knowing the difference. Otherwise compose.

## Dependency injection

- Constructor injection everywhere. A class receives its collaborators; it never constructs or looks them up.
- No module-level singletons, no global mutable state, no service locator.
- The composition root (`interfaces/bootstrap.py`) is the one place that maps interfaces to concrete implementations.
- A DI container such as `dependency-injector` is acceptable once wiring gets large, but the container stays in the composition root and never leaks into `core/` or `application/`.

## Design patterns

The list below is shared vocabulary, not a menu to pick from. The requirement decides the pattern; name the one you used and the requirement forcing it in the PR description. Repository, Unit of Work, and Adapter are not optional here — they are required by the persistence and third-party-client rules.

Strategy, Factory / Abstract Factory, Adapter, Facade, Template Method, Observer (domain events), Repository, Unit of Work, CQRS.

Implement the smallest version that satisfies the current requirement. A single implementation behind a Strategy interface is premature; add the interface when the second implementation arrives.
