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
poetry run lint-imports         # layer boundaries
poetry run pytest -q            # tests
```

If these commands fail because the project is not set up this way, follow [bootstrap](.agents/skills/python-workflow-and-tooling/references/bootstrap.md) to create or correct the configuration. Never work around it with `pip`, a `requirements.txt`, or a bare `pytest` call.

## Rules that apply to every task

- Dependencies point inward. `core/` imports nothing from `application/`, `infrastructure/`, or top-level `interfaces/`, and no third-party framework. `lint-imports` enforces this; a failure there is not a style nit.
- Full type hints on every signature, `mypy --strict` clean. No bare `except`.
- Match the ceremony to the change: a bugfix needs a fix and a regression test, not an ADR. See [workflow](.agents/skills/python-workflow-and-tooling/references/workflow.md) for what each tier requires.
- `interfaces` is two different things depending on path: `core/interfaces/` holds ABCs and Protocols, top-level `interfaces/` holds FastAPI routers, CLI, and controllers.

## Reference

The standards are three Agent Skills under `.agents/skills/`. An agent that supports skills loads them on its own from the descriptions; one that does not should open the `SKILL.md` below when the task touches its subject, and follow that file's own links into `references/`.

| Read it when the task involves | Skill |
| --- | --- |
| Layer placement, contracts, entities, DI, imports, mutable defaults, monolith vs service, comments, ADRs | [python-clean-architecture](.agents/skills/python-clean-architecture/SKILL.md) |
| Typing, docstrings, tests, persistence, endpoints, logging, security, performance | [python-code-conventions](.agents/skills/python-code-conventions/SKILL.md) |
| Sizing a change, the gate commands, dependencies, project setup | [python-workflow-and-tooling](.agents/skills/python-workflow-and-tooling/SKILL.md) |
