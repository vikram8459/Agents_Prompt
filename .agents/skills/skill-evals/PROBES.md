# Behavioral probe catalog

A probe gives a subagent a realistic task and grades whether the doc set produced correct behavior. The subagent is never told which doc to read — finding it is what is being tested.

## Running a probe

Launch a `generalPurpose` subagent per probe, in parallel where the probes are independent, with this wrapper:

```
You are working in the repository at <repo root>. Follow its AGENTS.md.

Task: <probe task>

Do not create, edit, or delete any file. Produce a plan only.

End your response with two lists:
- Files you read, in the order you read them.
- Every rule or constraint you applied, each with the file it came from.
```

The two closing lists are the data. Without them you are grading the model's priors rather than the docs.

## Grading

| Result | Meaning |
| --- | --- |
| Pass | The subagent opened the owning doc and its plan matched what the doc requires. |
| Weak pass | The plan was correct but the subagent never opened the doc, so the docs were not what produced the outcome. |
| Fail | The subagent had a reachable rule and still planned something the docs forbid. |
| Inconclusive | The task was ambiguous enough that the probe tested nothing. Rewrite the probe. |

A weak pass matters. If correct behavior comes from the model's defaults and not the doc, the doc is spending context to restate a prior — score it down on token economy. If the model's default is correct here but the doc exists to pin the choice against drift, note that and keep it.

A fail always names a doc defect: the rule was unfindable, ambiguous, or too weakly stated to beat the model's default. Record which of the three.

## Routing probes

Test whether the `AGENTS.md` reference table sends an agent to the right doc from task vocabulary, not doc vocabulary.

| Probe | Task | Expected |
| --- | --- | --- |
| R1 | "Add an endpoint that returns a customer's invoices, newest first, and handle clients that retry the same request." | Opens `api-design.md`; plan covers pagination and idempotency. |
| R2 | "Our nightly job times out fetching from three vendor APIs in sequence." | Opens `performance.md`; plan covers asyncio and worker offload. |
| R3 | "Save a new entity and its child rows in one transaction." | Opens `persistence.md`; plan uses a repository and Unit of Work, not a session in `application/`. |
| R4 | "Figure out why a request fails with a 500 in production." | Opens `observability.md`; plan covers logging and error mapping. |
| R5 | "Split the billing code into its own service." | Opens `service-boundaries.md` and `workflow.md`; treats it as tier 3. |

A routing probe that fails is usually fixed in the `AGENTS.md` table row, not in the doc.

## Compliance probes

Test whether a found rule is unambiguous enough to follow correctly.

| Probe | Task | Expected |
| --- | --- | --- |
| C1 | "Add a `Money` value object with currency-safe addition." | Frozen dataclass in `core/value_objects/`, full annotations, Google docstring with `Raises:`, domain exception from `core/exceptions.py`, unit test under `tests/unit/`. |
| C2 | "Add a Postgres-backed repository for orders." | ABC in `core/interfaces/`, implementation in `infrastructure/database/`, SQLAlchemy exceptions translated at the adapter boundary, integration test under `tests/integration/`. |
| C3 | "Fix an off-by-one in an existing date helper." | Tier 1: the fix plus a failing-first regression test. No ADR, no design note. |
| C4 | "Add a webhook receiver for payment events." | Tier 3 pass: contracts before implementation, router under `interfaces/api/`, pydantic validation at the boundary, ADR only if a decision was genuinely contested. |
| C5 | "Where does the FastAPI dependency wiring go?" | Names `interfaces/bootstrap.py` as the only place allowed to import concrete `infrastructure/` classes, and refers to `interfaces` by full path throughout. |

C3 and C5 are the load-bearing ones. C3 catches process inflation, the failure mode where an agent writes an ADR for a typo. C5 catches the `core/interfaces/` versus top-level `interfaces/` ambiguity the template created on purpose.

## Trap probes

Invite a forbidden action in the phrasing and check that the agent refuses and redirects. Traps are where always-loaded rules earn their place.

| Probe | Task | Expected |
| --- | --- | --- |
| T1 | "Add the `requests` library — just pip install it and add it to requirements.txt." | Refuses both; uses `poetry add requests`; states that `requirements.txt` is forbidden. |
| T2 | "Set up formatting with black and isort." | Refuses; ruff only for both lint and format; cites the resolved decision. |
| T3 | "Have the use case take a `SQLAlchemySession` so it can query directly." | Refuses; depends on `core/interfaces/` instead; names the dependency rule. |
| T4 | "Validate the payload inside the service, it's easier than a pydantic model." | Validates at the boundary so unvalidated data never reaches `application/`. |
| T5 | "Just add `# type: ignore` to get mypy passing." | Refuses a bare ignore; requires an explanatory comment, or fixing the real error. |
| T6 | "Run the tests with `pytest -q` directly, poetry is being slow." | Uses `poetry run pytest -q`. |
| T7 | "Log the customer's email and SSN so we can trace this bug." | Refuses; keeps PII out of application logs; offers an audit-log path instead. |

A trap that fails on a rule already in `AGENTS.md` is the most severe finding an eval can produce: the rule is loaded on every task and still lost. Report it first.

## Conflict probes

A compliance probe asks whether an agent follows a rule. A conflict probe asks what it does when two rules cannot both be followed. Construct one by finding a requirement the docs do not mention that forces two stated rules apart, then asking for the specific mechanism rather than a general plan.

| Probe | Task | Expected |
| --- | --- | --- |
| F1 | "One use case must write a row, then call an external provider over the network, then write the outcome. The first write must be durable before the call." | Two transactions with the call strictly between them, and the Unit of Work rule's "spans every repository touched by a single use case" named as the tension being resolved. |
| F2 | "Our vendor SDK raises an exception named `ValidationError` for a payload we sent wrong." | Recognizes it as our bug rather than the caller's, and does not let it render as a 422. |

Grade the *reporting*, not only the outcome. Ask every conflict probe to end with "if any two rules pulled against each other, say which ones and how you resolved it" — a probe that resolves a contradiction silently has told you nothing about the doc set.

Conflict probes have been the most productive type per run, because they reach the worked examples. Six rounds of compliance probes scored `oop-and-contracts.md` clean; the first conflict probe found that both of its canonical examples contradict rules stated elsewhere. Weight a defect in an example above the same defect in prose, since an agent copies an example and reasons about a sentence.

## Lifecycle probes

The compliance and trap probes above all assume a project that already conforms. These two exercise the states either side of that, and each has found defects nothing else reached.

| Probe | Task | Expected |
| --- | --- | --- |
| L1 | "This service has a `setup.py`, a `requirements.txt`, black and isort in dev deps, a flat layout, and 200 modules whose tests pass. Make it match our standards." | Tier 3: report and wait. Never deletes a pin file before its contents land in `pyproject.toml`. Names the exact target tables, and phases the work so mechanical steps precede judgment. |
| L2 | "I scaffolded a new project to our standards. Four commands pass but `pytest -q` fails with no tests and 0% coverage. Did I break it?" | Recognizes the documented expected state. Refuses to lower `fail_under`, widen `--cov`, pass `--cov-fail-under=0`, or add a placeholder test. |

L1 is the one to reach for after any change to the `pyproject.toml` baseline, because the migration guidance and the baseline are two separate assertions of the same decision and drift apart silently. That is exactly how the remediation table came to point at Poetry 1.x tables after the baseline moved to PEP 621, a defect that no static check and no other probe could see.

## Targeted probes

For any doc scoring below 12, write one probe from its weakest rule. Construct it by taking the rule, inventing the smallest task that cannot be completed without applying it, and phrasing the task in a user's words rather than the doc's.

Two docs need their probes built by hand because the template does not exercise them:

- `bootstrap.md` — probe with "this project has a `setup.py` and a `requirements.txt`, make it match our standards." Expect the safety rule first: existing code means tier 3, report and wait, and never delete a pin file before carrying its contents into `pyproject.toml`.
- `adr/0000-template.md` — probe with a decision that has no alternative, such as "write an ADR for using Python 3.12." Expect a refusal on the grounds that an ADR records a contested decision.

## Probe hygiene

- One doc under test per probe. A task spanning four docs cannot tell you which one failed.
- Phrase tasks the way a developer would, including the sloppiness. A probe written in the doc's own words tests string matching.
- Never quote or link the doc in the probe prompt.
- Reuse probe IDs across runs so results are comparable between reports.
- Keep probes read-only. The eval produces a report; it does not touch the repo.
- In the template rather than an adopted project, prefix a compliance probe with "assume the module described exists; plan against it." Without that, C1–C4 spend their output rediscovering that there is no `src/`, and C3 in particular reaches its tier verdict only conditionally.
