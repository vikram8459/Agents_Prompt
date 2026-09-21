---
name: python-clean-architecture
description: Place Python code in the correct clean-architecture layer and define its contracts. Covers the src/ package layout, the inward-only dependency rule, import placement, entities and value objects, mutable defaults and shared state, ABCs versus Protocols, dependency injection and the composition root, design pattern selection, the modular monolith versus service decision, the ADR format, and when a code comment is worth writing. Use when creating a module, entity, repository contract, or use case; when deciding which layer or package code belongs in; when choosing between an ABC and a Protocol; when wiring dependencies; when placing or deferring an import; when asked whether to extract a service; when writing an architecture decision record; or when deciding whether a comment says anything the code does not.
compatibility: Python 3.12 project managed with Poetry, using a src/ layout with core, application, infrastructure, interfaces, config, and utils packages.
---

# Python clean architecture

Four layers, and imports that only ever point inward:

```
interfaces/ ─┐
             ├──> application/ ──> core/
infrastructure/ ─┘
```

- `core/` — the domain. Imports the standard library and nothing else. No SQLAlchemy, no pydantic, no FastAPI.
- `application/` — use cases. Imports `core/`, and depends on `core/interfaces/` abstractions rather than any concrete adapter.
- `infrastructure/` — adapters that implement `core/interfaces/`.
- `interfaces/` (top level) — delivery: HTTP routers, CLI, workers. Nothing imports from here except the composition root.

A violation is a bug even if the code runs, and `poetry run lint-imports` fails on it.

## The one naming trap

The word names two different directories — `core/interfaces/` and top-level `interfaces/` — so always resolve it by full path and never by the bare word:

- `core/interfaces/` — abstract contracts such as `ThingRepository` and `UnitOfWork`.
- `interfaces/` at the top level — the delivery layer.

## Decide in this order

1. **Which layer?** Domain rules go in `core/`, orchestration in `application/`, anything touching a database, queue, or third-party API in `infrastructure/`, anything a user or client talks to in top-level `interfaces/`. See [layout](references/layout.md) for the full tree and the per-package split.
2. **What is the contract?** Define the ABC or Protocol in `core/interfaces/` before writing an implementation. See [OOP and contracts](references/oop-and-contracts.md) for the ABC-versus-Protocol rule, entity and value object definitions, injection rules, and the pattern list.
3. **One service or several?** Default to a modular monolith and extract only for a concrete driver. See [service boundaries](references/service-boundaries.md).
4. **Does this decision need recording?** Apply the test before reaching for the format: an ADR records a decision where a real alternative was rejected for a stated reason. If there was no genuine alternative, the ADR should not exist and the template is not worth opening. If the test passes, follow [the ADR template](references/adr-template.md) and write to `docs/adr/NNNN-slug.md`.

## Non-negotiables

- Enforce invariants in constructors and at public method boundaries, so an object cannot exist in an invalid state.
- Constructor injection everywhere. A class receives its collaborators and never constructs or looks them up. No module-level singletons, no global mutable state, no service locator.
- No mutable default arguments. A `[]`, `{}`, or `set()` in a signature is built once when the function is defined and shared by every call that omits it, so one call's mutation shows up in the next. Default to `()` with a `Sequence` annotation when the parameter is read-only, or to `None` when absent and empty mean different things. See [no mutable defaults](references/no-mutable-defaults.md) for the class-attribute, shared-constant, and dataclass-field versions of the same bug, which ruff's `B006` does not catch.
- `interfaces/bootstrap.py` is the composition root and the only module allowed to import concrete classes from `infrastructure/`. It sits above the delivery surfaces, not inside one, so a gRPC-only or worker-only service still has exactly one wiring module.
- A third-party client is imported only inside `infrastructure/`, behind a contract in `core/interfaces/`: database drivers in `infrastructure/database/`, outbound HTTP clients in `infrastructure/external_apis/`, cache in `infrastructure/cache/`, brokers in `infrastructure/messaging/`. The vendor's types, identifiers, and exceptions stop at that boundary.
- Every import sits at the top of the file, after the module docstring and `from __future__ import annotations`, so a module's dependencies read as one block instead of hiding in a function body. A deferred import does not escape `lint-imports` either, which parses the module rather than the call graph. See [imports](references/imports.md) for the one narrow exception, the `TYPE_CHECKING` rule, and why a local import never resolves a cycle.
- Value objects are `@dataclass(frozen=True)` with equality by value; entities have identity plus behavior and equality by ID.
- Keep each interface to one responsibility. A five-method interface whose callers use two should be two interfaces.
- Implement the smallest version of a pattern that satisfies the current requirement. A single implementation behind a Strategy interface is premature.
- Group by feature within a layer, not by type across layers. If two packages import each other, they are one package.
- A comment earns its place only by carrying what the code cannot: why an invariant exists, which alternative was rejected, what external constraint forces an awkward line. A comment that narrates the statement below it is noise that goes stale on the next edit — self-documenting code needs a better name, not a caption. Docstrings on public API are a separate obligation and stay required. See [comments](references/comments.md) for the test to apply, the categories that qualify, and what each layer's comments are usually about.

## Related skills

- Repository and Unit of Work details, ORM isolation, pydantic at the edge: the `python-code-conventions` skill.
- Which change tier a new module implies, and what it must ship with: the `python-workflow-and-tooling` skill.
