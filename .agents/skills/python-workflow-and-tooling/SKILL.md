---
name: python-workflow-and-tooling
description: Size a change, run the right quality gates, and configure or repair a Python project's tooling. Covers the three change tiers and what each must deliver, the five gate commands, coverage and import-boundary enforcement, SemVer, the Poetry and PEP 621 pyproject baseline, ruff and mypy and pytest and import-linter configuration, pre-commit hooks, and bootstrapping or migrating a non-conforming project. Use when deciding how much process a change needs, when a gate command fails, when adding a dependency, when setting up a new project, or when the existing setup uses pip, requirements.txt, black, or isort.
compatibility: Python 3.12 managed with Poetry 2 and a committed poetry.lock. Assumes ruff, mypy, pytest, and import-linter as the only quality tools; no black, no isort, no pip.
---

# Python workflow and tooling

## Pick the tier before writing anything

| Tier | Trigger | Deliver |
| --- | --- | --- |
| Bootstrap | An empty project, no source under version control | The `tooling.md` baseline, created directly. No design note, no ADR, and no regression test — there is no behavior to regress. Expect `pytest -q` to fail until the first module lands. An existing codebase is tier 3 instead, whatever is non-conforming. |
| 1 | A fix inside an existing module, adding no public contract | The fix, a regression test that fails without it, lint and types clean. No design note, no ADR. |
| 2 | A new feature in an existing module | Tier 1, plus a short design note in the PR description, docstrings on new public functions and classes, and an updated API schema if an endpoint changed. |
| 3 | A new module or service, or a change to a public contract | Tier 2, plus the full design pass: model the domain, define contracts first, place code in the right layer, decide monolith or service, name each pattern and the requirement forcing it, test at every warranted level, and document. |

Match the ceremony to the change. A bugfix needs a test, not an ADR, and an ADR records only a decision that was genuinely contested. See [workflow](references/workflow.md) for the full tier definitions, the design pass steps, and the versioning rule.

## The five gates

```bash
poetry run ruff check --fix .   # lint + import sorting
poetry run ruff format .        # formatting (no black, no isort)
poetry run mypy --strict src    # typecheck
poetry run lint-imports         # layer boundaries
poetry run pytest -q            # tests
```

A merge is blocked on any failure, on `core/` or `application/` coverage below 90%, and on a `# noqa` or `# type: ignore` without an explanatory comment. `lint-imports` is the one that enforces the inward dependency rule; a failure there is an architecture defect, not a style nit.

## Dependencies

Poetry only, with `poetry.lock` committed in the same commit as any `pyproject.toml` dependency change.

```bash
poetry install                  # includes dev group
poetry add <pkg>                # runtime dep
poetry add --group dev <pkg>    # dev dep
poetry lock                     # after a manual pyproject edit
```

Never `pip install`, and never create a `requirements.txt`. Review what a new dependency pulls in before adding it.

## When the setup does not match

If the gate commands fail because the project is configured differently, follow [bootstrap](references/bootstrap.md) rather than working around it. Its safety rule comes first: an empty project is created directly with tier 1 ceremony, while an existing codebase is tier 3 — report what is non-conforming and get agreement before rewriting dependency management, moving packages, or deleting files. Never delete a lockfile, `requirements.txt`, or `setup.py` until its contents are carried into `pyproject.toml`.

For the `pyproject.toml` baseline, the ruff and mypy settings, the import-linter contracts, and the pre-commit config, see [tooling](references/tooling.md). Two details bite most often: metadata belongs in the PEP 621 `[project]` table because Poetry 2 deprecated `[tool.poetry.name]`, and `requires-python` takes a PEP 440 specifier — `>=3.12,<4.0`, not a caret.

## Ambiguity

State assumptions explicitly and proceed. Ask only when the question actually blocks the work and you cannot pick a defensible default.

## Related skills

- Which layer code belongs in and how to define its contracts: the `python-clean-architecture` skill.
- Typing, docstrings, tests, and the per-topic conventions: the `python-code-conventions` skill.
