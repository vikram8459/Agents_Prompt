# OOP and contracts

## Building blocks

| Concept | Rule |
| --- | --- |
| Entity | Identity plus behavior. Mutable. Equality by ID. |
| Value object | Immutable (`@dataclass(frozen=True)`). Equality by value. |
| Domain service | Stateless. Orchestrates entities and value objects. Use only when the logic belongs to no single entity. |
| Repository | Interface in `core/interfaces/`, implementation in `infrastructure/`. |
| Use case | One public entry point in `application/use_cases/`, takes a command DTO plus injected dependencies. |

Enforce invariants in constructors and at public method boundaries, so an object cannot exist in an invalid state.

## ABC or Protocol

- `abc.ABC` with `@abstractmethod` when implementations should inherit and you want the base class to reject incomplete subclasses at instantiation.
- `typing.Protocol` for structural typing across package boundaries, and when the implementer should not have to import your package.

Keep each interface to one responsibility. A five-method interface where callers use two methods should be two interfaces.

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional, Protocol


class ThingRepository(ABC):
    """Persistence contract for `Thing` aggregates."""

    @abstractmethod
    def get(self, thing_id: str) -> Optional[object]:
        """Return the thing with `thing_id`, or None if absent."""

    @abstractmethod
    def add(self, thing: object) -> None:
        """Persist a new thing."""

    @abstractmethod
    def list(self) -> Iterable[object]:
        """Return all things."""


class UnitOfWork(Protocol):
    """Transactional boundary around one or more repositories."""

    repo: ThingRepository

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
```

## Use case shape

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateThingCommand:
    """Input for creating a thing."""

    name: str


def execute(cmd: CreateThingCommand, uow: UnitOfWork) -> object:
    """Create and persist a thing, returning the stored representation."""
    new_thing = {"id": "generated", "name": cmd.name}
    with uow:
        uow.repo.add(new_thing)
        uow.commit()
    return new_thing
```

## Composition over inheritance

Inherit only for genuine subtype relationships that satisfy Liskov substitution: any caller holding the base type must work with the subtype without knowing the difference. Otherwise compose.

## Dependency injection

- Constructor injection everywhere. A class receives its collaborators; it never constructs or looks them up.
- No module-level singletons, no global mutable state, no service locator.
- The composition root (`interfaces/api/bootstrap.py`) is the one place that maps interfaces to concrete implementations.
- A DI container such as `dependency-injector` is acceptable once wiring gets large, but the container stays in the composition root and never leaks into `core/` or `application/`.

## Design patterns

Reach for these when the requirement calls for them, and say in the PR description why:

Strategy, Factory / Abstract Factory, Adapter, Facade, Template Method, Observer (domain events), Repository, Unit of Work, CQRS.

Implement the smallest version that satisfies the current requirement. A single implementation behind a Strategy interface is premature; add the interface when the second implementation arrives.
