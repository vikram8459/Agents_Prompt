# Imports

The import block is a module's dependency list. A reader should be able to see every layer and every third-party package a module depends on without scrolling past the first screen, because that block is where a dependency-rule violation is visible to a human.

## Placement

Every import goes at the top of the file, in this order and nothing interleaved:

1. The module docstring.
2. `from __future__ import annotations`, in any module using forward references.
3. Imports, in the stdlib / third-party / first-party grouping ruff's `I` rules apply.
4. Everything else — constants, classes, functions.

Ruff's `E402` catches an import placed after other module-level code. Nothing in the rule set flags an import buried inside a function or a method, which is the case this rule exists for.

## Deferred imports

A function-local import does not escape `lint-imports`. It parses each module's syntax tree rather than its call graph, so the edge is recorded wherever the statement sits. Moving an import into a function hides a layer violation from the reviewer without making it legal, and that is the main reason to refuse one.

Two situations are sometimes offered as justification. Only the second is:

- **Breaking an import cycle.** Not a fix here. A cycle between two packages means they are one package, and a cycle between layers means the dependency rule is already broken — see [layout](layout.md) for both. Restructure instead.
- **A genuinely expensive or optional dependency** that most calls never touch. Allowed inside `infrastructure/` only, where third-party clients already live, and it carries a comment stating what the deferral buys. That comment is the "justification a rule demands" category in [comments](comments.md); without it the next reader has no way to tell the deferral from a mistake.

The composition root is not an exception. `interfaces/bootstrap.py` imports concrete `infrastructure/` classes at module top like any other module — it is the one place allowed to name them, so there is nothing to hide.

## Form

- Absolute imports from the distribution package root: `from myproject.core.entities.thing import Thing`. No relative imports.
- No wildcard imports. `from x import *` defeats both `lint-imports` and the reader.
- Import the module or the name you use, not a package you then attribute-walk through.

## Typing-only imports

An import used solely in annotations belongs in an `if TYPE_CHECKING:` block at the top of the file, paired with `from __future__ import annotations` so the annotation stays a string at runtime. This keeps a type reference from becoming a real dependency edge.

It has one failure mode worth knowing: anything that resolves annotations at runtime — pydantic models, FastAPI route signatures, SQLAlchemy mapped classes — raises `NameError` on a name that only exists under `TYPE_CHECKING`. Those all live in `infrastructure/` and top-level `interfaces/`, so the rule in practice is that a `TYPE_CHECKING` import is safe in `core/` and `application/`, and needs checking anywhere a framework reads the annotations.

A `TYPE_CHECKING` block is also not a way around the dependency rule. `core/` importing a SQLAlchemy type for an annotation is still `core/` knowing about SQLAlchemy.
