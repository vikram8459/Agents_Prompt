# Python agent standards template

A reusable set of agent instructions for Python services built on clean architecture, packaged as three Agent Skills. Copy `AGENTS.md` and `.agents/skills/` into a project; they are written to be read by a coding agent, not as prose documentation.

This repository is the template. It intentionally contains no `pyproject.toml`, no `src/`, and no code — the commands in `AGENTS.md` describe the project you copy it into, not this one.

## Structure

`AGENTS.md` is the only file loaded on every task. It holds the project description, the runtime and package manager, the five commands, and the four rules that apply to everything. Everything else lives in three skills, each a `SKILL.md` router over its own `references/`, so an agent reads a topic only when the task touches it. That split is the point: a 250-line always-loaded instruction file spends context on persistence rules during a CSS change.

```
AGENTS.md
.agents/skills/
├── python-clean-architecture/     layout, OOP and contracts, imports,
│                                  no mutable defaults, service boundaries,
│                                  comments, ADR template
├── python-code-conventions/       python-style, testing, persistence,
│                                  api-design, observability, security,
│                                  performance
├── python-workflow-and-tooling/   workflow, tooling, bootstrap
└── skill-evals/                   grades the three skills above
```

Skills load in three stages: every `SKILL.md` description is in context from the start, the body is read when the agent judges the skill relevant, and a `references/` file is opened only when the router points at it. So descriptions are written to be matched against task wording, and the routers carry the rules an agent needs before it knows which reference it wants.

## Portability

`.agents/skills/` is the vendor-neutral location, so these work beyond any one tool. Cursor reads it, and also reads `.claude/skills/` and `.codex/skills/`, at both project and user scope. To use the skills with a client that only scans its own directory, copy or link the three directories there. Each `SKILL.md` carries only specification fields — `name`, `description`, and `compatibility` — so any conforming client can load them; `skill-evals` additionally sets `disable-model-invocation`, a Cursor and Claude extension that other clients ignore.

For an agent whose harness has no skills support at all, `AGENTS.md` still routes: its table links the three `SKILL.md` files directly.

## Adopting it in a project

1. Copy `AGENTS.md` and `.agents/skills/` to the project root.
2. Replace the `[TODO: PROJECT DESCRIPTION NOT FILLED IN]` line at the top of `AGENTS.md` with one sentence naming what the service does and the domain it owns. Name the domain, not the architecture — an agent uses this line to guess where things go and what the existing entities are called.
3. Ask the agent to follow [bootstrap.md](.agents/skills/python-workflow-and-tooling/references/bootstrap.md). It checks the project against every requirement here and then creates what is missing or migrates what was set up differently, so a new project gets its `pyproject.toml`, layer directories, and pre-commit config without you assembling them by hand.
4. Confirm the four static gates in `AGENTS.md` run clean afterwards: `ruff check`, `ruff format`, `mypy --strict src`, and `lint-imports`. `pytest -q` is expected to fail on a bare scaffold, since no tests are collected and coverage of `core/` and `application/` is 0% against the 90% floor; it goes green with your first module and its test, and bootstrap says so. A command that fails *unexpectedly* on the first try teaches agents to improvise, which is how you end up with the `pip install` and hand-written `requirements.txt` the file explicitly forbids.
5. Delete any reference file whose subject the project does not have, and remove its row from the owning `SKILL.md`. If there is no message queue, `service-boundaries.md` is noise, and a pointer to it is a link an agent may follow for nothing.

On an existing codebase, bootstrap treats migration as a tier 3 change: it reports what it wants to change and waits, rather than rewriting a working build unprompted.

## Decisions baked in

These were contested in the source document and have been resolved one way throughout. Changing one means changing it in `AGENTS.md` and in the relevant skill together, or the contradiction comes back.

| Decision | Choice |
| --- | --- |
| Runtime | Python 3.12 |
| Dependency manager | Poetry with a committed `poetry.lock`; no `setup.py`, no `requirements*.txt` |
| Lint and format | Ruff only; black and isort are not used |
| Typecheck | `mypy --strict` on `src/` |
| Layer boundaries | `import-linter` contracts in `pyproject.toml`, run as `lint-imports`; ruff's `banned-api` cannot scope a ban per layer without a config file in each one |
| Docstrings | Google style, enforced by ruff's `D` rules |
| Domain layer | `src/{project_name}/core/`, alongside `config/` and `utils/` |
| `interfaces` | Deliberately two directories: `core/interfaces/` for contracts, top-level `interfaces/` for delivery. Always refer to it by full path |
| Process | Three tiers by change size |
| Coverage gate | 90% on `core/` and `application/` |

## Maintaining the template

Keep `AGENTS.md` short. Before adding a line to it, ask whether it is true of every task; if not, it belongs in a `skills/` file. Anything an agent already knows — that PEP 8 exists, that clean code is good — belongs in neither.
