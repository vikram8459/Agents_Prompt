# Tooling

All tool configuration lives in `pyproject.toml`. Do not add `setup.cfg`, `.flake8`, `.isort.cfg`, or a black config; there is nothing left for them to configure.

## Baseline pyproject.toml

Target Python 3.12. A new project starts from this and adds only what it needs.

```toml
[tool.poetry]
name = "{project-name}"
version = "0.1.0"
packages = [{ include = "{project_name}", from = "src" }]

[tool.poetry.dependencies]
python = "^3.12"

[tool.poetry.group.dev.dependencies]
ruff = "*"
mypy = "*"
pytest = "*"
pytest-cov = "*"

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

[tool.pytest.ini_options]
addopts = "-q --cov=src --cov-report=term-missing"
testpaths = ["tests"]

[tool.coverage.report]
fail_under = 90

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

The `D` and `ANN` rule sets are what actually enforce the docstring and typing requirements in [python-style](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/python-style.md); without them those are suggestions. They are switched off under `tests/` because test functions do not need docstrings or annotated fixtures to be readable.

`fail_under = 90` applies to the whole run here. To gate only `core/` and `application/` as [testing](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/testing.md) specifies, narrow `--cov` to those packages in the CI test step rather than loosening this number.

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

## Pre-commit

Hooks run `ruff check`, `ruff format`, and `mypy` on changed files.

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
        args: [--strict]
        files: ^src/
```

Pin `rev` to a real release and bump it deliberately; `pre-commit autoupdate` on every run makes the hook behave differently for different people.

Do not run the full test suite in a pre-commit hook. It makes every commit slow enough that people start passing `--no-verify`, which loses the fast checks too. CI runs the suite.

## CI

The pipeline should run, on every pull request: lint, typecheck, test with coverage, build the artifact, upload the coverage report. Failures block the merge.

No CI platform is specified yet, so there is no pipeline file in this template. When the platform is chosen, add its config here and remove this paragraph. Until then, do not invent one.
