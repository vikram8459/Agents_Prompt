# Python agent standards template

A reusable set of agent instructions for Python services built on clean architecture. Copy `AGENTS.md` and `skills/` into a project; they are written to be read by a coding agent, not as prose documentation.

This repository is the template. It intentionally contains no `pyproject.toml`, no `src/`, and no code — the commands in `AGENTS.md` describe the project you copy it into, not this one.

## Structure

`AGENTS.md` is the only file loaded on every task. It holds the project description, the runtime and package manager, the four commands, and the four rules that apply to everything. Everything else lives in `skills/` and is linked from a table at the bottom, so an agent reads a topic only when the task touches it. That split is the point: a 250-line always-loaded instruction file spends context on persistence rules during a CSS change.

```
AGENTS.md
skills/
├── architecture/    layout, OOP and contracts, service boundaries, adr/
├── conventions/     python-style, testing, persistence, api-design,
│                    observability, security, performance
└── guides/          workflow, tooling
```

## Adopting it in a project

1. Copy `AGENTS.md` and `skills/` to the project root.
2. Replace the `[TODO: PROJECT DESCRIPTION NOT FILLED IN]` line at the top of `AGENTS.md` with one sentence naming what the service does and the domain it owns. Name the domain, not the architecture — an agent uses this line to guess where things go and what the existing entities are called.
3. Ask the agent to follow [skills/guides/bootstrap.md](skills/guides/bootstrap.md). It checks the project against every requirement here and then creates what is missing or migrates what was set up differently, so a new project gets its `pyproject.toml`, layer directories, and pre-commit config without you assembling them by hand.
4. Confirm all four commands in `AGENTS.md` actually run afterwards. A command that fails on the first try teaches agents to improvise, which is how you end up with the `pip install` and hand-written `requirements.txt` the file explicitly forbids.
5. Delete any reference file whose subject the project does not have. If there is no message queue, `service-boundaries.md` is noise, and its row in the table is a link an agent may follow for nothing.

On an existing codebase, bootstrap treats migration as a tier 3 change: it reports what it wants to change and waits, rather than rewriting a working build unprompted.

## Decisions baked in

These were contested in the source document and have been resolved one way throughout. Changing one means changing it in `AGENTS.md` and in the relevant `skills/` file together, or the contradiction comes back.

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

## Maintaining the template

Keep `AGENTS.md` short. Before adding a line to it, ask whether it is true of every task; if not, it belongs in a `skills/` file. Anything an agent already knows — that PEP 8 exists, that clean code is good — belongs in neither.
