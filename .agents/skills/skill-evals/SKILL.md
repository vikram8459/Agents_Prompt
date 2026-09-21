---
name: skill-evals
description: Evaluate and score the Agent Skills under .agents/skills/ and the AGENTS.md entrypoint, using a static audit followed by behavioral probes, and write a scored report to evals/. Use when the user asks to eval, evaluate, audit, score, grade, or review the skills directory, the reference docs, or the agent instructions in this template.
compatibility: Requires Python 3.12 on PATH for the audit script, which uses only the standard library. Expects skills under .agents/skills/ and an AGENTS.md at the repo root.
disable-model-invocation: true
---

# Skill evals

The docs under `.agents/skills/` are instructions read by a coding agent, not prose documentation. They are only worth their context cost if an agent can find the right one and act on it without further guessing. This skill measures that in two phases: a static audit of every doc, then behavioral probes that check whether the docs actually drive correct behavior.

Phase 1 finds what is wrong on the page. Phase 2 finds what is wrong in practice — a rule can read well and still be unfindable or ambiguous in a live task. Run both; phase 2 targets the weaknesses phase 1 surfaces.

## Workflow

Copy this checklist and track progress:

```
Skill eval progress:
- [ ] Step 1: Inventory and mechanical audit
- [ ] Step 1b: Lint the examples against the project's own gates
- [ ] Step 2: Score each doc against the rubric
- [ ] Step 3: Cross-doc consistency pass
- [ ] Step 4: Select and run behavioral probes
- [ ] Step 5: Write the report
```

### Step 1: Inventory and mechanical audit

Run the audit script from the repo root. It is stdlib-only; no install step.

```bash
python .agents/skills/skill-evals/scripts/audit_docs.py
```

It reports, per doc: size, heading structure, concrete anchors (code blocks, tables, paths), unresolved relative links, orphan status against the link graph rooted at `AGENTS.md`, hedge-phrase hits, and which docs share each load-bearing claim. Use `--format json` when you want to quote exact numbers into the report.

Treat its output as measurements, not verdicts. An orphan doc is a finding; a hedge phrase may be legitimate.

Hold the script to the standards it measures: run `mypy --strict` and `ruff check` over `scripts/` in the same step. A failure there is a finding about the eval rather than about the docs, and it is the kind that goes unnoticed for exactly as long as nobody looks.

### Step 1b: Lint the examples against the project's own gates

Every Python example in the doc set is code an agent will copy, so check it the way the project checks code rather than by reading it. Create a temp project outside the repository, give it the `pyproject.toml` baseline the docs prescribe, transcribe each example into a module, and run `ruff check` and `mypy --strict` over them.

Write any scaffolding the examples need — module docstrings, placeholder types, an enclosing class for a snippet — to conform, so that a diagnostic pointing at scaffolding is your fault and everything else is a doc defect. Report each diagnostic as either a genuine defect or an artifact of the example being a fragment; a missing return in a signature-only excerpt is the latter.

This step needs no judgment and is the cheapest finding-per-minute in the eval. Prose can only be judged against other prose, and two reviewers can disagree; an example can be judged against the project's configured tooling, which cannot be argued with.

### Step 2: Score each doc against the rubric

Read every `SKILL.md` and reference file under `.agents/skills/` in full, then score each on the six rubric dimensions. See [RUBRIC.md](RUBRIC.md) for the dimensions, the 0–3 scale, and worked examples of each score.

Score `AGENTS.md` too. It is the only always-loaded file and the router for everything else, so its failures cost more than any single doc's.

For each dimension below 3, record the specific line or rule at fault and the concrete edit that would raise it. "Vague in places" is not a finding; "the `Cohesion` section's 'keep cross-package imports few' gives no threshold, so it cannot be applied or violated" is.

### Step 3: Cross-doc consistency pass

The template's stated design is that a decision lives in one place, and changing it means changing `AGENTS.md` and the owning doc together. Verify that held. For each load-bearing claim the script groups by doc, confirm the docs agree on the number, the path, and the tool:

- Coverage threshold and which layers it gates
- Python version and the ruff `target-version`
- Which tools are mandated versus forbidden (ruff, mypy, pytest, poetry; black, isort, pip, `requirements.txt`)
- Layer names and the direction of the dependency rule
- Which tier a given kind of change is, especially where two docs assign tiers
- The `core/interfaces/` versus top-level `interfaces/` distinction, which must never appear as a bare word

A contradiction between two docs is a higher-severity finding than any single doc's score, because the agent that reads only one of them gets it wrong with full confidence.

### Step 4: Select and run behavioral probes

Pick probes from [PROBES.md](PROBES.md): at minimum one routing probe, one compliance probe, and one trap probe, plus a targeted probe for every doc that scored below 12. Run each in a fresh `generalPurpose` subagent so no context from this session leaks in, and run independent probes in parallel.

Grade the transcript, not the prose: which docs did the subagent open, and did its plan match what the docs require? A probe fails when the subagent had access to a rule and still got it wrong — that is a doc defect, not a model defect.

Probes are read-only. Instruct each subagent to plan and cite, never to create or edit files.

### Step 5: Write the report

Write to `evals/skills-eval-<YYYY-MM-DD>.md` using the template below, creating `evals/` if it does not exist. If an earlier report exists there, read the most recent one and add a column comparing each doc's total to its previous total, so scores are tracked over time rather than re-litigated. On a first run there is nothing to compare, so drop the `Prev` column and say the report is the baseline.

Then summarize in chat: the overall verdict in one sentence, the three highest-severity findings, and the top fix. Do not paste the tables into chat; link the report.

## Report template

```markdown
# Skill eval — <YYYY-MM-DD>

Docs evaluated: <n> under `.agents/skills/`, plus `AGENTS.md`. Probes run: <n>.

## Verdict

<Two or three sentences: the state of the doc set, the dominant failure mode, and whether anything blocks an agent from working correctly today.>

## Scores

| Doc | Actionable | Consistent | Discoverable | Scoped | Token economy | Concrete | Total | Prev |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AGENTS.md | 3 | 3 | 3 | 2 | 3 | 3 | 17/18 | 16 |

Bands: 16–18 solid, 12–15 minor fixes, 8–11 needs work, below 8 rewrite.

## Findings

Ordered by severity. Each finding names the file, the rule at fault, and the edit that fixes it.

### 1. <Severity>: <one-line summary>
**Where:** `.agents/skills/<skill>/<path>.md`, <section or line>
**Problem:** <what an agent does wrong because of this>
**Fix:** <the concrete edit>

## Cross-doc consistency

| Claim | Docs asserting it | Agree? | Notes |
| --- | --- | --- | --- |

## Probe results

| Probe | Type | Expected | Observed | Result |
| --- | --- | --- | --- | --- |

## Fix list

1. <Highest-value edit, with the file it touches.>
```

## Scope rules

- Evaluate the instructions as instructions. This repo is a template with no `src/` and no `pyproject.toml` by design, so the absence of code is never a finding.
- The unfilled `[TODO: PROJECT DESCRIPTION NOT FILLED IN]` line in `AGENTS.md` is correct in the template and a finding only in a project that adopted it. The audit script flags it either way; decide which repo you are in before reporting it.
- Judge a doc against what `AGENTS.md` claims it covers. A doc is not incomplete for omitting a topic another doc owns.
- Do not fix anything during the eval. Report the edit; apply it only when the user asks. A graded report the user can disagree with is worth more than silent rewrites.
- Length is not a defect by itself. A long doc that is dense with paths, commands, and tables scores better on token economy than a short one made of principles.

## Additional resources

- Scoring dimensions, scale, and worked examples: [RUBRIC.md](RUBRIC.md)
- Probe catalog with prompts and expected behavior: [PROBES.md](PROBES.md)
- Mechanical audit script: `scripts/audit_docs.py`
