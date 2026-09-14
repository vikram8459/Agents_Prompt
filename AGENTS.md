# AGENTS.md

**[TODO: PROJECT DESCRIPTION NOT FILLED IN]** — replace this line with one sentence naming what this service does and the domain it owns, for example "Billing API that issues invoices and reconciles payments against Stripe." Do not describe the architecture here; that is covered below.

If you are an agent and this line still reads `[TODO: ...]`, say so before making assumptions about the domain.

## Runtime and package manager

Python 3.12, Poetry. Never invoke `pip install` and never create a `requirements.txt`.

```bash
poetry install                  # includes dev group
poetry add <pkg>                # runtime dep, updates poetry.lock
poetry add --group dev <pkg>    # dev dep
```

## Commands

```bash
poetry run ruff check --fix .   # lint + import sorting
poetry run ruff format .        # formatting (no black, no isort)
poetry run mypy --strict src    # typecheck
poetry run pytest -q            # tests
```

If these commands fail because the project is not set up this way, follow [bootstrap](skills/guides/bootstrap.md) to create or correct the configuration. Never work around it with `pip`, a `requirements.txt`, or a bare `pytest` call.

## Rules that apply to every task

- Dependencies point inward. `core/` imports nothing from `application/`, `infrastructure/`, or `interfaces/`, and no third-party framework.
- Full type hints on every signature, `mypy --strict` clean. No bare `except`.
- Match the ceremony to the change: a bugfix needs a fix and a regression test, not an ADR. See [workflow](skills/guides/workflow.md) for what each tier requires.
- `interfaces` is two different things depending on path: `core/interfaces/` holds ABCs and Protocols, top-level `interfaces/` holds FastAPI routers, CLI, and controllers.

## Reference

Read these only when the task touches them.

| Topic | File |
| --- | --- |
| Package layout, layer boundaries | [skills/architecture/layout.md](skills/architecture/layout.md) |
| Entities, ABCs vs Protocols, DI, design patterns | [skills/architecture/oop-and-contracts.md](skills/architecture/oop-and-contracts.md) |
| Modular monolith vs services, messaging | [skills/architecture/service-boundaries.md](skills/architecture/service-boundaries.md) |
| Naming, docstrings, typing details | [skills/conventions/python-style.md](skills/conventions/python-style.md) |
| Test layout, coverage targets, mocking | [skills/conventions/testing.md](skills/conventions/testing.md) |
| Repositories, Unit of Work, SQLAlchemy, Alembic | [skills/conventions/persistence.md](skills/conventions/persistence.md) |
| FastAPI, pydantic, gRPC, pagination, idempotency | [skills/conventions/api-design.md](skills/conventions/api-design.md) |
| Settings, logging, error mapping, metrics, tracing | [skills/conventions/observability.md](skills/conventions/observability.md) |
| Secrets, PII, input validation | [skills/conventions/security.md](skills/conventions/security.md) |
| asyncio, worker offload, caching | [skills/conventions/performance.md](skills/conventions/performance.md) |
| Change tiers, deliverables, quality gates | [skills/guides/workflow.md](skills/guides/workflow.md) |
| Tool configuration, pyproject baseline, pre-commit | [skills/guides/tooling.md](skills/guides/tooling.md) |
| Setting up or correcting a project's tooling | [skills/guides/bootstrap.md](skills/guides/bootstrap.md) |
