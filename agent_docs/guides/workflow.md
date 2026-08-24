# Change workflow

Process scales with the change. Pick the tier first.

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
2. **Define contracts first.** ABCs and Protocols in `core/interfaces/`, before implementations. See [OOP and contracts](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/architecture/oop-and-contracts.md).
3. **Place code in the right layer.** See [layout](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/architecture/layout.md).
4. **Decide monolith or service** if that is in question. See [service boundaries](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/architecture/service-boundaries.md).
5. **Choose patterns with a stated reason.** Name the pattern and the requirement forcing it.
6. **Implement.**
7. **Test** at unit, integration, and e2e level as the change warrants. See [testing](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/conventions/testing.md).
8. **Document**: an ADR in this project's own `docs/architecture/adr/`, from the [ADR template](https://raw.githubusercontent.com/vikram8459/Agents_Prompt/main/agent_docs/architecture/adr/0000-template.md), plus README updates and a dependency sketch if the layer graph changed.

An ADR records a decision that was genuinely contested — why this option, what was rejected, what it costs. Do not write one for a decision with no alternative.

## Quality gates

Every tier, enforced by pre-commit locally and CI on the branch:

```bash
poetry run ruff check --fix .
poetry run ruff format .
poetry run mypy --strict src
poetry run pytest -q
```

A merge is blocked on any failure, on `core/` or `application/` coverage below 90%, and on a `# noqa` or `# type: ignore` without an explanatory comment.

## Versioning

SemVer on the public API. A breaking change bumps the major version and ships with migration notes describing what callers must change.

## Ambiguity

State assumptions explicitly and proceed. Ask only when the question actually blocks the work and you cannot pick a defensible default.
