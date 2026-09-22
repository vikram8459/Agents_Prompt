# Bootstrapping and conformance

Run this when the standards in `AGENTS.md` do not match the project you are in — either because nothing is set up yet, or because the project was set up a different way.

## Safety rule first

Check whether the project already has source code under version control.

- **Empty or new project** — create everything below directly. Tier 1 ceremony: no design note, no ADR, and no regression test, since there is nothing to regress.
- **Existing project with code** — this is a tier 3 change. Report what is non-conforming and what you propose to change, and get agreement before rewriting dependency management, moving packages, or deleting files. Migrating a working project's build is not a cleanup task you do in passing.

Never delete a lockfile, a `requirements.txt`, or a `setup.py` until its contents have been carried into `pyproject.toml`.

Deleting `requirements.txt` also breaks anything that installs from it. Grep the Dockerfile, CI config, and deploy scripts for `pip install -r` before the file goes, and move each to `poetry install` in the same change. Regenerating the file with `poetry export` is not an available workaround — `AGENTS.md` forbids the file existing, not merely being hand-written.

## Detect

Work through this in order and record what is missing or wrong.

| Check | Conforming state |
| --- | --- |
| `pyproject.toml` | Exists, uses the Poetry build backend, and declares `[project]` with `requires-python = ">=3.12,<4.0"`. `poetry check` passes with no deprecation warning |
| `poetry.lock` | Exists and is committed |
| `src/` layout | Packages under `src/{project_name}/`, not at the repo root |
| Layer directories | `core/` and `application/` always, since the layers contract requires them; `infrastructure/`, top-level `interfaces/`, `config/`, `utils/` when the project uses them |
| `tests/` | `unit/`, `integration/`, `e2e/`, `fixtures/`, mirroring `src/`, each an importable package with an `__init__.py` |
| Ruff config | `target-version = "py312"`, `D` and `ANN` selected, pydocstyle convention `google` |
| mypy config | `strict = true` over `src`, plus the `tests.*` override from [tooling.md](tooling.md) |
| Coverage gate | `--cov` narrowed to `core/` and `application/`, failing under 90% for those two and gating nothing else |
| Import contracts | `[tool.importlinter]` holds the layers contract from [tooling.md](tooling.md), plus the forbidden contract naming this project's I/O and framework packages once it has one, and `lint-imports` passes |
| `.pre-commit-config.yaml` | Exists, runs ruff and mypy through the project environment rather than a pinned mirror repo, does not run the test suite |
| `.env.example` | Exists and lists every setting read by `config/settings.py` |
| Forbidden files | None of `requirements.txt`, `requirements-dev.txt`, `setup.py`, `setup.cfg`, `.flake8`, `.isort.cfg` |
| Forbidden dev deps | Neither `black` nor `isort` |

## Create what is missing

Take `pyproject.toml` from the baseline in [tooling.md](tooling.md), substituting the project name, then `poetry install` to generate `poetry.lock`.

Create the layer and test directories from `layout.md` in the `python-clean-architecture` skill, each with an `__init__.py`. Do not create a layer the project has no use for yet; an empty `infrastructure/messaging/` is clutter that implies a queue exists.

Create `.pre-commit-config.yaml` from the snippet in [tooling.md](tooling.md), then run `poetry run pre-commit install` once. This requires the project to be a git repository; if it is not, say so rather than running `git init` unprompted.

CI is deliberately not specified. Do not invent a pipeline file.

## Fix what is non-conforming

| Found | Remediation |
| --- | --- |
| `requirements.txt` / `requirements-dev.txt` | Move each pin into `[project.dependencies]` or the dev group, run `poetry lock`, verify the install, then delete the file |
| `setup.py` | Move name and version into `[project]`, consumer-facing extras into `[project.optional-dependencies]`, a tooling extra such as `dev` or `test` into `[tool.poetry.group.dev.dependencies]`, console scripts into `[project.scripts]`, and the package mapping into `[tool.poetry]`. Delete only once the Poetry build produces the same distribution — build the sdist and wheel and compare contents first |
| `.pre-commit-config.yaml` using `ruff-pre-commit` or `mirrors-mypy` | Replace with the `repo: local` hooks from [tooling.md](tooling.md) so hook and gate share one tool version. Run the hooks once afterwards: a mirror pinned behind the lockfile will have been enforcing removed rules, and a `mirrors-mypy` hook will have been failing on every third-party import |
| `black` or `isort` in dev deps | Remove both, run `ruff format .` once across the repo, and commit that reformatting on its own so it does not obscure a real diff |
| `.flake8`, `.isort.cfg`, lint sections in `setup.cfg` | Delete; move any deliberate rule exclusion into `[tool.ruff.lint]` with a comment saying why |
| Ruff missing `D` or `ANN` | Add them. Expect a large number of new findings on existing code — fix them per module rather than in one sweep, or the review is unreadable |
| mypy not strict | Enable `strict = true`. If existing code cannot pass, do not weaken the global setting; add a narrow per-module override with a comment and a plan |
| Flat package layout | Move to `src/` and update the Poetry `packages` entry. Run the test suite before and after; an import that resolved by accident from the repo root will break |
| No import contracts | Add the layers contract from [tooling.md](tooling.md), add the forbidden contract if the project has I/O or framework packages to name, and run `lint-imports` once to see the real state |
| `lint-imports` reports violations on existing code | Report the count and the worst offenders, and get agreement before rewriting. Reversing an import direction means introducing an interface and injecting it, not moving a file, so each one is a design change rather than a cleanup |

## Report

Finish by stating what was created, what was changed, and anything left non-conforming with the reason. If you skipped a remediation because it needed agreement, say which one.

A conforming fresh scaffold is not fully green, and that is the expected end state. `ruff check`, `ruff format`, `mypy --strict src`, and `lint-imports` all pass on an empty project. `pytest -q` does not: with no tests collected it exits non-zero, and coverage of `core/` and `application/` is 0% against the 90% floor. This resolves with the first module and its test. Report it as expected rather than broken, and do not lower `fail_under`, widen `--cov`, or add a placeholder test to make it pass.
