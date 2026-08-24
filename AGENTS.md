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

If these commands fail because the project is not set up this way, follow [bootstrap](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/guides/bootstrap.md) to create or correct the configuration. Never work around it with `pip`, a `requirements.txt`, or a bare `pytest` call.

## Rules that apply to every task

- Dependencies point inward. `core/` imports nothing from `application/`, `infrastructure/`, or `interfaces/`, and no third-party framework.
- Full type hints on every signature, `mypy --strict` clean. No bare `except`.
- Match the ceremony to the change: a bugfix needs a fix and a regression test, not an ADR. See [workflow](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/guides/workflow.md) for what each tier requires.
- `interfaces` is two different things depending on path: `core/interfaces/` holds ABCs and Protocols, top-level `interfaces/` holds FastAPI routers, CLI, and controllers.

## Reference

These files are not in this repository. They live in the shared standards repo and are fetched on demand, so read one only when the task touches its topic.

Fetch a URL with your web-fetch tool, or `curl -fsSL <url>` if you have none. Do not copy, vendor, or commit these files into this project; the URL is the source of truth and tracks the latest version.

If a fetch fails, say so and stop. Do not substitute a convention from memory — the whole point of the link is that this project's rules may differ from the defaults you would otherwise assume.

| Topic | Fetch |
| --- | --- |
| Package layout, layer boundaries | [layout](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/architecture/layout.md) |
| Entities, ABCs vs Protocols, DI, design patterns | [oop-and-contracts](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/architecture/oop-and-contracts.md) |
| Modular monolith vs services, messaging | [service-boundaries](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/architecture/service-boundaries.md) |
| Naming, docstrings, typing details | [python-style](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/python-style.md) |
| Test layout, coverage targets, mocking | [testing](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/testing.md) |
| Repositories, Unit of Work, SQLAlchemy, Alembic | [persistence](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/persistence.md) |
| FastAPI, pydantic, gRPC, pagination, idempotency | [api-design](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/api-design.md) |
| Settings, logging, error mapping, metrics, tracing | [observability](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/observability.md) |
| Secrets, PII, input validation | [security](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/security.md) |
| asyncio, worker offload, caching | [performance](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/performance.md) |
| Change tiers, deliverables, quality gates | [workflow](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/guides/workflow.md) |
| Tool configuration, pyproject baseline, pre-commit | [tooling](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/guides/tooling.md) |
| Setting up or correcting a project's tooling | [bootstrap](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/guides/bootstrap.md) |
