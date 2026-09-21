# Tooling

All tool configuration lives in `pyproject.toml`. Do not add `setup.cfg`, `.flake8`, `.isort.cfg`, or a black config; there is nothing left for them to configure.

## Baseline pyproject.toml

Target Python 3.12. A new project starts from this and adds only what it needs.

Metadata goes in the PEP 621 `[project]` table. Poetry 2 deprecated `[tool.poetry.name]` and `[tool.poetry.version]`, and `poetry check` warns about both, so `[tool.poetry]` now carries only what PEP 621 has no field for — the `packages` entry and the dependency groups. Note that `requires-python` takes a PEP 440 specifier: `>=3.12,<4.0`, not the `^3.12` caret that Poetry's own dependency syntax accepts. `poetry add` writes runtime dependencies into `[project.dependencies]` and `poetry add --group dev` into the group below.

```toml
[project]
name = "{project-name}"
version = "0.1.0"
requires-python = ">=3.12,<4.0"
dependencies = []

[tool.poetry]
packages = [{ include = "{project_name}", from = "src" }]

[tool.poetry.group.dev.dependencies]
ruff = "*"
mypy = "*"
pytest = "*"
pytest-cov = "*"
pytest-asyncio = "*"
import-linter = "*"
pre-commit = "*"

[tool.ruff]
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "ARG", "PTH", "D", "ANN"]

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["D", "ANN", "ARG"]

[tool.mypy]
python_version = "3.12"
strict = true
files = ["src"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
disallow_untyped_calls = false

[tool.pytest.ini_options]
addopts = "-q --cov=src/{project_name}/core --cov=src/{project_name}/application --cov-report=term-missing"
testpaths = ["tests"]

[tool.coverage.report]
fail_under = 90

[tool.importlinter]
root_package = "{project_name}"
include_external_packages = true

[[tool.importlinter.contracts]]
name = "Dependencies point inward"
type = "layers"
layers = [
    "({project_name}.interfaces) | ({project_name}.infrastructure)",
    "{project_name}.application",
    "{project_name}.core",
]
ignore_imports = ["{project_name}.interfaces.bootstrap -> {project_name}.infrastructure.**"]
unmatched_ignore_imports_alerting = "none"

[[tool.importlinter.contracts]]
name = "core is framework-free"
type = "forbidden"
source_modules = ["{project_name}.core"]
forbidden_modules = ["sqlalchemy", "pydantic", "fastapi", "httpx"]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

The `D` and `ANN` rule sets are what actually enforce the docstring and typing requirements in `python-style.md` in the `python-code-conventions` skill; without them those are suggestions. They are switched off under `tests/` because test functions do not need docstrings or annotated fixtures to be readable.

The `tests.*` mypy override is the other half of that decision. `mypy --strict src` never reaches `tests/`, but `testing.md` in the `python-code-conventions` skill asks for a wider `mypy --strict src tests` run after a contract change, and without the override that run buries the real finding under one `no-untyped-def` per test function — the exact functions `ANN` deliberately exempts. Relaxing those two settings and nothing else keeps every structural check, so a fake that has fallen behind its contract still fails. The override matches on module path, so it silently does nothing unless `tests/` and each subdirectory carry an `__init__.py`; without them mypy names the module `test_thing` rather than `tests.unit.test_thing` and the pattern never matches.

`pytest-asyncio` is in the group because the `core/interfaces/` contracts are async, which makes use case tests coroutines. Without it pytest collects an async test, warns, and skips — a suite that reports green having executed nothing, with the coverage gate satisfied by tests that never ran. Mark each async test `@pytest.mark.asyncio` rather than setting `asyncio_mode = "auto"`, so the dependency is visible at the call site.

`--cov` is narrowed to `core/` and `application/` so `fail_under = 90` gates exactly what `testing.md` in the `python-code-conventions` skill specifies and nothing else. Coverage elsewhere is still worth looking at — `poetry run pytest --cov=src` when you want the whole picture — but it does not block a merge. Do not widen `--cov` back to `src` in the baseline; that turns integration coverage into a merge gate, which is the thing testing.md argues against.

## Poetry

The only dependency manager. `poetry.lock` is committed and must be in the same commit as any `pyproject.toml` dependency change.

```bash
poetry install
poetry add <pkg>
poetry add --group dev <pkg>
poetry lock            # after a manual pyproject edit
```

Runtime dependencies stay out of the dev group. No `pip install` into the environment.

## Ruff

Ruff is both linter and formatter and also handles import sorting, replacing black and isort entirely.

```bash
poetry run ruff check --fix .
poetry run ruff format .
```

Disabling a rule requires a comment giving the reason, either at the `# noqa` site or next to the ignore entry in `pyproject.toml`.

## mypy

`poetry run mypy --strict src`. Strict mode is the gate, not an aspiration — new code lands clean.

## Import boundaries

`lint-imports` is what makes the dependency rule in `layout.md` in the `python-clean-architecture` skill a gate instead of a convention. Ruff cannot do this job: `banned-api` is not scoped per directory, and a nested config that scopes it replaces the parent's ban list rather than extending it, so enforcing the rule with ruff means one config file per layer with the bans duplicated in each.

```bash
poetry run lint-imports
```

The layers contract puts `{project_name}.interfaces` and `{project_name}.infrastructure` on one line separated by a pipe, which makes them independent siblings: neither may import the other, and both may import `application` and `core`. The parentheses mark those two optional, so a worker-only service or one with no adapters yet does not have to carry an empty package to satisfy the contract. `application` and `core` are deliberately not optional: every service has both, so a missing one is a typo or a moved package rather than a design choice, and the `Missing layer` error is the point. The one documented exception — the composition root importing concrete adapters — is the single `ignore_imports` entry, so a second exception is a visible decision rather than quiet drift. `unmatched_ignore_imports_alerting = "none"` keeps the contract passing on a project whose `bootstrap.py` has no infrastructure imports yet.

`config/` and `utils/` are deliberately absent from the layers list. They are cross-cutting and imported from several layers, so ordering them would be a lie; the `forbidden` contract is what stops them dragging a framework into `core/`.

This is not a pre-commit hook. Building the import graph needs the package installed, and it is a whole-graph check that a partial commit cannot answer meaningfully. The local command and CI cover it.

## Pre-commit

Hooks run `ruff check`, `ruff format`, and `mypy` through the project's own environment.

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff check
        entry: poetry run ruff check --fix
        language: system
        types: [python]
      - id: ruff-format
        name: ruff format
        entry: poetry run ruff format
        language: system
        types: [python]
      - id: mypy
        name: mypy
        entry: poetry run mypy --strict src
        language: system
        pass_filenames: false
        types: [python]
```

These are `repo: local` hooks, and the absent `rev` is the point: `poetry.lock` is the single place a tool version is decided. The mirror repositories `ruff-pre-commit` and `mirrors-mypy` each carry their own pin, and those pins drift from the lockfile. A hook pinned to an older ruff enforces rules the gate has since dropped — `ANN101` is the usual way this is found, because ruff removed it and it fires on every method in the codebase, so the hook rejects code `poetry run ruff check` accepts.

`mirrors-mypy` has a further problem that no pin fixes. It installs mypy into an isolated environment holding mypy and nothing else, so `--strict` cannot resolve `sqlalchemy`, `pydantic`, or `fastapi`, and fails `import-not-found` on every adapter and every router unless the whole runtime dependency list is restated under `additional_dependencies`.

`pass_filenames: false` on the mypy hook is deliberate. mypy over an arbitrary subset of changed files answers a different question than mypy over `src`, and the gate asks the second one.

Do not run the full test suite in a pre-commit hook. It makes every commit slow enough that people start passing `--no-verify`, which loses the fast checks too. CI runs the suite.

## CI

The pipeline should run, on every pull request: lint, typecheck, check import boundaries, test with coverage, build the artifact, upload the coverage report. Failures block the merge.

No CI platform is specified yet, so there is no pipeline file in this template. When the platform is chosen, add its config here and remove this paragraph. Until then, do not invent one.
