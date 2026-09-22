# Package layout

`src/` layout, installed editable via `poetry install`.

```
project_root/
├── src/
│   └── {project_name}/
│       ├── core/                  # Domain. Depends on nothing.
│       │   ├── entities/          # Identity + behavior
│       │   ├── value_objects/     # Immutable, equality by value
│       │   ├── interfaces/        # ABCs and Protocols (contracts)
│       │   └── exceptions.py      # Domain exceptions
│       ├── application/           # Use cases. Depends on core only.
│       │   ├── services/
│       │   ├── use_cases/
│       │   └── dto/
│       ├── infrastructure/        # Adapters. Implements core interfaces.
│       │   ├── database/
│       │   ├── messaging/
│       │   ├── cache/
│       │   └── external_apis/
│       ├── interfaces/            # Delivery. HTTP, gRPC, CLI, workers.
│       │   ├── api/
│       │   ├── grpc/
│       │   ├── worker/
│       │   ├── cli/
│       │   └── gui/
│       ├── config/
│       │   ├── settings.py
│       │   └── constants.py
│       └── utils/                 # Cross-cutting: logging, decorators
├── tests/                         # Mirrors src layout
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── .agents/skills/                # Agent Skills holding these standards
│   ├── python-clean-architecture/
│   ├── python-code-conventions/
│   └── python-workflow-and-tooling/
├── docs/adr/                      # Architecture decision records
├── contracts/                     # Published .proto or OpenAPI snapshots, if any
├── scripts/
├── pyproject.toml
├── poetry.lock
├── .env.example
└── README.md
```

There is no `setup.py`, no `requirements.txt`, and no `requirements-dev.txt`. `pyproject.toml` plus `poetry.lock` is the whole story.

## The two `interfaces` directories

This name is deliberately reused, so resolve it by path, never by the bare word:

- `core/interfaces/` — abstract contracts (`ThingRepository`, `UnitOfWork`). Imported by `application/` and implemented by `infrastructure/`.
- `interfaces/` (top level) — the delivery layer. HTTP routers, CLI commands, serializers. Nothing imports from here except the composition root.

When writing or referring to one in prose, always include the full path.

## Dependency rule

Imports point inward only:

```
interfaces/ ─┐
             ├──> application/ ──> core/
infrastructure/ ─┘
```

- `core/` imports the standard library and third-party libraries that compute in-process. It does not import an I/O client, a web framework, or an ORM, and no vendor type appears in an entity, a value object, or a `core/interfaces/` signature; those libraries are adapters and live in `infrastructure/`. The `forbidden` contract in `tooling.md` names the packages this project keeps out.
- `application/` imports `core/`. It depends on `core/interfaces/` abstractions, never on a concrete adapter.
- `infrastructure/` imports `core/` to implement its interfaces.
- Only the composition root (`interfaces/bootstrap.py`) is allowed to import concrete classes from `infrastructure/`. It sits above the delivery surfaces rather than inside one, so a service with no HTTP API still has exactly one wiring module.

A violation of this rule is a bug even if the code runs. `poetry run lint-imports` is what checks it; the contracts that encode this diagram live in `pyproject.toml` and are given in `tooling.md` in the `python-workflow-and-tooling` skill.

## Cohesion

Group by feature within a layer, not by type across layers. Keep cross-package imports one-directional; if two packages import each other, they are one package.
