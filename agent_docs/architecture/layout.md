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
│       ├── interfaces/            # Delivery. FastAPI, CLI, GUI.
│       │   ├── api/
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
├── docs/
│   └── architecture/adr/          # This project's own ADRs
├── scripts/
├── AGENTS.md                      # The only local standards file
├── pyproject.toml
├── poetry.lock
├── .env.example
└── README.md
```

There is no `setup.py`, no `requirements.txt`, and no `requirements-dev.txt`. `pyproject.toml` plus `poetry.lock` is the whole story.

There is also no `agent_docs/` directory here. The standards you are reading are fetched from the shared repo at the URLs listed in `AGENTS.md`; only `AGENTS.md` itself is checked into a project. Do not create a local copy of them.

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

- `core/` imports from the standard library and nothing else. No SQLAlchemy, no pydantic, no FastAPI.
- `application/` imports `core/`. It depends on `core/interfaces/` abstractions, never on a concrete adapter.
- `infrastructure/` imports `core/` to implement its interfaces.
- Only the composition root (`interfaces/api/bootstrap.py`) is allowed to import concrete classes from `infrastructure/`.

A violation of this rule is a bug even if the code runs.

## Cohesion

Group by feature within a layer, not by type across layers. Keep cross-package imports few and one-directional; if two packages import each other, they are one package.
