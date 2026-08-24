# Bootstrapping and conformance

Run this when the standards in `AGENTS.md` do not match the project you are in — either because nothing is set up yet, or because the project was set up a different way.

## Safety rule first

Check whether the project already has source code under version control.

- **Empty or new project** — create everything below directly. This is a tier 1 change.
- **Existing project with code** — this is a tier 3 change. Report what is non-conforming and what you propose to change, and get agreement before rewriting dependency management, moving packages, or deleting files. Migrating a working project's build is not a cleanup task you do in passing.

Never delete a lockfile, a `requirements.txt`, or a `setup.py` until its contents have been carried into `pyproject.toml`.

## Detect

Work through this in order and record what is missing or wrong.

| Check | Conforming state |
| --- | --- |
| `pyproject.toml` | Exists, uses the Poetry build backend, `requires-python = "^3.12"` |
| `poetry.lock` | Exists and is committed |
| `src/` layout | Packages under `src/{project_name}/`, not at the repo root |
| Layer directories | `core/`, `application/`, `infrastructure/`, `interfaces/`, `config/`, `utils/` |
| `tests/` | `unit/`, `integration/`, `e2e/`, `fixtures/`, mirroring `src/` |
| Ruff config | `target-version = "py312"`, `D` and `ANN` selected, pydocstyle convention `google` |
| mypy config | `strict = true` over `src` |
| Coverage gate | Fails under 90% for `core/` and `application/` |
| `.pre-commit-config.yaml` | Exists, runs ruff and mypy, does not run the test suite |
| `.env.example` | Exists and lists every setting read by `config/settings.py` |
| Forbidden files | None of `requirements.txt`, `requirements-dev.txt`, `setup.py`, `setup.cfg`, `.flake8`, `.isort.cfg` |
| Forbidden dev deps | Neither `black` nor `isort` |

## Create what is missing

Take `pyproject.toml` from the baseline in [tooling](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/guides/tooling.md), substituting the project name, then `poetry install` to generate `poetry.lock`.

Create the layer and test directories from [layout](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/architecture/layout.md), each with an `__init__.py`. Do not create a layer the project has no use for yet; an empty `infrastructure/messaging/` is clutter that implies a queue exists.

Create `.pre-commit-config.yaml` from the snippet in [tooling](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/guides/tooling.md), then run `pre-commit install` once. This requires the project to be a git repository; if it is not, say so rather than running `git init` unprompted.

CI is deliberately not specified. Do not invent a pipeline file.

## Fix what is non-conforming

| Found | Remediation |
| --- | --- |
| `requirements.txt` / `requirements-dev.txt` | Move each pin into `[tool.poetry.dependencies]` or the dev group, run `poetry lock`, verify the install, then delete the file |
| `setup.py` | Move name, version, and packages into `[tool.poetry]`; delete once the Poetry build produces the same distribution |
| `black` or `isort` in dev deps | Remove both, run `ruff format .` once across the repo, and commit that reformatting on its own so it does not obscure a real diff |
| `.flake8`, `.isort.cfg`, lint sections in `setup.cfg` | Delete; move any deliberate rule exclusion into `[tool.ruff.lint]` with a comment saying why |
| Ruff missing `D` or `ANN` | Add them. Expect a large number of new findings on existing code — fix them per module rather than in one sweep, or the review is unreadable |
| mypy not strict | Enable `strict = true`. If existing code cannot pass, do not weaken the global setting; add a narrow per-module override with a comment and a plan |
| Flat package layout | Move to `src/` and update the Poetry `packages` entry. Run the test suite before and after; an import that resolved by accident from the repo root will break |

## Report

Finish by stating what was created, what was changed, and anything left non-conforming with the reason. If you skipped a remediation because it needed agreement, say which one.
