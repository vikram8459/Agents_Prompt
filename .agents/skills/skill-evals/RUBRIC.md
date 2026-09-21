# Scoring rubric

Six dimensions, each scored 0–3, for a total of 18 per doc.

| Score | Meaning |
| --- | --- |
| 3 | No defect on this dimension. |
| 2 | One local defect; a named edit fixes it. |
| 1 | A recurring defect that changes how an agent behaves. |
| 0 | The dimension fails outright. |

Bands: 16–18 solid, 12–15 minor fixes, 8–11 needs work, below 8 rewrite.

Examples below are drawn from this template's own docs so the standard is calibrated against real text rather than invented samples.

---

## 1. Actionable and enforceable

Every rule states an action an agent can take or a decision it can make, and a reviewer can tell whether it was followed.

Ask of each rule: what would a violation look like? If you cannot describe one, the rule is decoration.

**3 —** `layout.md`: "`core/` imports from the standard library and nothing else. No SQLAlchemy, no pydantic, no FastAPI." A violation is a single import line. Enforceable by reading the file.

**2 —** `layout.md`'s `Cohesion` section: "Keep cross-package imports few and one-directional." The second half is checkable; "few" has no threshold, so an agent cannot tell whether it complied. One local fix: drop "few" or name a number.

**1 —** A doc where most rules read "prefer", "consider", or "where appropriate" without stating the default to use when nothing in particular applies.

**0 —** A doc made of principles an agent cannot convert into an action: "write maintainable code", "keep coupling low".

Note the difference between hedging and deliberate discretion. `testing.md`'s "Reach for Hypothesis on pure functions with interesting input spaces — parsers, money arithmetic, date handling — not on everything" hedges the boundary on purpose but names three qualifying cases and one exclusion, so it stays actionable. That scores 3, not 2.

## 2. Consistent

The doc does not contradict `AGENTS.md` or a sibling doc, and it does not contradict itself.

Check the load-bearing claims the audit script groups by doc: the coverage number, the Python version, the mandated and forbidden tools, the layer names, the tier assignments.

**3 —** `testing.md` gates coverage at 90% on `core/` and `application/`; `workflow.md` blocks merges below 90% on the same two layers; `bootstrap.md` lists the same gate. Three docs, one number, same scope.

**2 —** A doc that repeats a rule correctly but in different words than the owning doc, so a later edit to one will silently diverge. Fix by replacing the restatement with a link.

**1 —** Two sections of the same doc assign the same change to different tiers.

**0 —** The doc states a decision the resolved-decisions table in `README.md` rejected, such as a `requirements.txt` workflow or black alongside ruff.

Self-consistency includes the `core/interfaces/` versus top-level `interfaces/` split. Any bare use of the word without a path is a consistency defect, because it is the one ambiguity the doc set deliberately created.

## 3. Discoverable

An agent reaches this doc at the moment it needs it, and every link in it resolves.

For a `SKILL.md`, the test is its frontmatter `description`: it must name both what the skill does and the task vocabulary that should trigger it, since that description is the only part loaded before activation. For a reference file, the test is that its owning `SKILL.md` links it with a line saying when to open it, and that the file's own outbound links resolve.

**3 —** `persistence.md` is linked from the conventions router's table row "Repositories, Unit of Work, SQLAlchemy, Alembic migrations". An agent writing a repository matches on those nouns without having to guess.

**2 —** A reference that is linked but whose pointer describes the file's structure rather than the task that should trigger it — "reference material on data" instead of naming the tools and patterns.

**1 —** A reference reachable only from a sibling reference, never from its `SKILL.md`. An agent finds it only after already picking the right neighbor.

**0 —** An unlinked file, or a doc whose links are dead. Both mean the content is not in play during a task.

Judge trigger wording from the task side. Read the description or the pointer and ask what task phrasing would make an agent open it; if the answer is "one that already uses the doc's own vocabulary", it is written from the wrong direction.

## 4. Scoped

One topic per doc, and the content sits in the file that owns it.

**3 —** `security.md` covers secrets, input validation, PII, and dependency risk. Four sections, one subject, nothing another doc owns.

**2 —** A doc with one section that belongs elsewhere — a test-layout rule inside `persistence.md`, for example. Fix by moving it and linking.

**1 —** A doc covering two subjects that should be two files, or restating enough of a neighbor that the two must be edited together.

**0 —** Content that belongs in `AGENTS.md` because it is true of every task, buried in a doc an agent reads only sometimes.

The inverse also applies to `AGENTS.md` itself: a line there that is not true of every task costs context on every unrelated task and should be scored down under this dimension.

## 5. Token economy

The doc spends context only on what the agent does not already know.

The test is not length. It is whether each paragraph would change the behavior of a competent agent that had never read it. Restating PEP 8, explaining what a repository pattern is, or arguing that tests are good all fail this.

**3 —** `python-style.md` opens by saying ruff already enforces PEP 8 and import order, then covers only the decisions ruff cannot make. It declares what it is not spending tokens on.

**2 —** A doc with one explanatory paragraph that teaches a concept the model already has, before getting to the project-specific rule.

**1 —** Sustained justification of rules an agent would follow anyway, or the same rule restated in three sections.

**0 —** A doc that could be deleted with no change in agent behavior.

A rationale sentence is worth its tokens when the rule is counterintuitive and an agent would otherwise "improve" on it. `testing.md` explains that coverage elsewhere is not gated "because integration coverage is a poor proxy for correctness" — that sentence prevents an agent from helpfully adding a gate. Keep it.

## 6. Concrete

Rules are anchored to paths, commands, code, or tables rather than described in prose.

**3 —** `bootstrap.md`'s detect and remediate tables: each row is a check, a conforming state, and the fix. Nothing to interpret.

**2 —** A rule that is correct but unanchored, naming no path, command, or example where one obviously applies.

**1 —** A doc that is mostly prose paragraphs where its subject calls for a table or a code block.

**0 —** No paths, no commands, no examples anywhere.

Prefer the anchor the agent will act on. A docstring rule with the example docstring beside it, as in `python-style.md`, removes a whole round of guessing about format.
