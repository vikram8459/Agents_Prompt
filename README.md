# Python agent standards

Agent instructions for Python services built on clean architecture, written to be read by a coding agent rather than as prose documentation.

A project installs **one file**: `AGENTS.md`. The reference topics stay here and are fetched over HTTPS when a task actually touches them, so adopting these standards adds a single file to a repo and updating them requires no change in any consumer.

This repository holds no `pyproject.toml`, no `src/`, and no code. The commands in `AGENTS.md` describe the project you install it into, not this one.

## Install

```powershell
iwr https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/AGENTS.md -OutFile AGENTS.md
```

```bash
curl -fsSL https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/AGENTS.md -o AGENTS.md
```

Git cannot clone a single file, so fetching the raw URL is the equivalent. Commit the result to your project.

## How it works

`AGENTS.md` is the only file an agent loads on every task. It holds the project description, runtime and package manager, the four commands, and the four rules that apply to everything. Every other topic is a row in a table of raw URLs at the bottom, fetched on demand.

That split is the point. A 250-line always-loaded instruction file spends context on persistence rules during a CSS change, and keeping the topics remote means a project never carries a copy that can drift.

| Topic | Source |
| --- | --- |
| Package layout, layer boundaries | [layout.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/architecture/layout.md) |
| Entities, ABCs vs Protocols, DI, patterns | [oop-and-contracts.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/architecture/oop-and-contracts.md) |
| Monolith vs services, messaging | [service-boundaries.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/architecture/service-boundaries.md) |
| ADR template | [0000-template.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/architecture/adr/0000-template.md) |
| Naming, docstrings, typing | [python-style.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/conventions/python-style.md) |
| Test layout, coverage, mocking | [testing.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/conventions/testing.md) |
| Repositories, Unit of Work, Alembic | [persistence.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/conventions/persistence.md) |
| FastAPI, pydantic, gRPC, idempotency | [api-design.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/conventions/api-design.md) |
| Settings, logging, errors, metrics | [observability.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/conventions/observability.md) |
| Secrets, PII, input validation | [security.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/conventions/security.md) |
| asyncio, workers, caching | [performance.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/conventions/performance.md) |
| Change tiers, quality gates | [workflow.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/guides/workflow.md) |
| Tool config, pyproject baseline | [tooling.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/guides/tooling.md) |
| Setting up or fixing a project | [bootstrap.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/guides/bootstrap.md) |

## After installing

1. Replace the `[TODO: PROJECT DESCRIPTION NOT FILLED IN]` line at the top of `AGENTS.md` with one sentence naming what the service does and the domain it owns. Name the domain, not the architecture — an agent uses this line to guess where things go and what the existing entities are called.
2. Ask the agent to follow [bootstrap.md](https://github.com/vikram8459/Agents_Prompt/blob/main/agent_docs/guides/bootstrap.md). It checks the project against every requirement here, then creates what is missing or migrates what was set up differently, so you get `pyproject.toml`, the layer directories, and the pre-commit config without assembling them by hand.
3. Confirm all four commands in `AGENTS.md` run afterwards. A command that fails on the first try teaches agents to improvise, which is how you end up with the `pip install` and hand-written `requirements.txt` the file explicitly forbids.

On an existing codebase, bootstrap treats migration as a tier 3 change: it reports what it wants to change and waits, rather than rewriting a working build unprompted.

## Versioning

The URLs in `AGENTS.md` track `main`, so an edit here reaches every project on its next fetch. That is convenient and it is also the main risk: there is no per-project pin. To freeze a project, replace `main` with a tag or commit SHA in that project's `AGENTS.md` URLs.

Two consequences worth accepting deliberately. An agent that is offline or blocked from `raw.githubusercontent.com` cannot read any topic, so `AGENTS.md` instructs it to say so and stop rather than fall back on remembered conventions. And each topic read costs a network round trip, which is why the table tells the agent to fetch only what the task touches.

## Maintaining this repo

Keep `AGENTS.md` short. Before adding a line to it, ask whether it is true of every task; if not, it belongs in a topic file. Anything an agent already knows — that PEP 8 exists, that clean code is good — belongs in neither.

Links between topic files are absolute raw URLs, not relative paths. A raw fetch returns bare markdown with no notion of its own location, so a relative link is a dead end for an agent. New cross-references must follow that pattern.

The decisions below were contested in the source material and are resolved one way throughout. Changing one means changing it in `AGENTS.md` and in the relevant topic file together, or the contradiction comes back.

| Decision | Choice |
| --- | --- |
| Runtime | Python 3.12 |
| Dependency manager | Poetry with a committed `poetry.lock`; no `setup.py`, no `requirements*.txt` |
| Lint and format | Ruff only; black and isort are not used |
| Typecheck | `mypy --strict` on `src/` |
| Docstrings | Google style, enforced by ruff's `D` rules |
| Domain layer | `src/{project_name}/core/`, alongside `config/` and `utils/` |
| `interfaces` | Deliberately two directories: `core/interfaces/` for contracts, top-level `interfaces/` for delivery. Always refer to it by full path |
| Process | Three tiers by change size; a bugfix needs a test, not an ADR |
| Coverage gate | 90% on `core/` and `application/` |
| CI platform | Not chosen; agents must not invent a pipeline file |
