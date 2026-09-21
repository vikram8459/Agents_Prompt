# Change workflow

Process scales with the change. Pick the tier first.

## Bootstrap — empty project

No source under version control yet: create the baseline from `tooling.md` directly.

Deliver the configuration and the layer and test directories, with lint and types clean. No design note, no ADR, and no regression test, because there is no behavior to regress; `pytest -q` is expected to fail until the first module and its test land. An existing codebase is tier 3 instead, whatever is non-conforming — see `bootstrap.md`.

## Tier 1 — Bugfix or small change

A fix inside an existing module that adds no new public contract.

Deliver: the fix, a regression test that fails without it, lint and types clean.

Do not write a design summary or an ADR for this tier.

## Tier 2 — New feature in an existing module

Deliver everything from tier 1, plus:

- A short design note in the PR description: which components change and why.
- Docstrings on new public functions and classes.
- Updated API schema if an endpoint changed.

## Tier 3 — New module, new service, or a change to a public contract

Deliver everything from tier 2, plus the full design pass:

1. **Model the domain.** Identify entities, value objects, services, repositories, use cases, and the invariants each must hold. Write down the inputs, outputs, and error cases at every boundary.
2. **Define contracts first.** ABCs and Protocols in `core/interfaces/`, before implementations. See `oop-and-contracts.md` in the `python-clean-architecture` skill.
3. **Place code in the right layer.** See `layout.md` in the same skill.
4. **Decide monolith or service** if that is in question. See `service-boundaries.md`, also there.
5. **Choose patterns with a stated reason.** Name the pattern and the requirement forcing it.
6. **Implement.**
7. **Test** at unit, integration, and e2e level as the change warrants. See `testing.md` in the `python-code-conventions` skill.
8. **Document**: README updates, and a dependency sketch if the layer graph changed.

An ADR is not a standing tier 3 deliverable, which is why it is absent from the list above. Apply the test before reaching for the format: an ADR records a decision where a real alternative was rejected for a stated reason — why this option, what was rejected, what it costs. Most tier 3 changes have no such alternative, and then the ADR should not exist. When the test does pass, write `docs/adr/NNNN-slug.md`, numbered from the highest existing ADR and following `adr-template.md` in the `python-clean-architecture` skill.

## Quality gates

Every tier, enforced by pre-commit locally and CI on the branch:

```bash
poetry run ruff check --fix .
poetry run ruff format .
poetry run mypy --strict src
poetry run lint-imports
poetry run pytest -q
```

A merge is blocked on any failure, on `core/` or `application/` coverage below 90%, and on a `# noqa` or `# type: ignore` without an explanatory comment.

## Versioning

SemVer on the public API. A breaking change bumps the major version and ships with migration notes describing what callers must change.

## Ambiguity

State assumptions explicitly and proceed. Ask only when the question actually blocks the work and you cannot pick a defensible default.
