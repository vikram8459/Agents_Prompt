"""Mechanical audit of the Agent Skills under ``.agents/skills/``.

Measures structure, link health, reachability from the entrypoint, frontmatter
conformance against the Agent Skills specification, and the spread of
load-bearing claims across docs. Reports measurements only; the judgment calls
belong to the rubric.

Standard library only. Run from the repo root::

    python .agents/skills/skill-evals/scripts/audit_docs.py
    python .agents/skills/skill-evals/scripts/audit_docs.py --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import deque
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Final, TypedDict

LINK_PATTERN: Final = re.compile(r"\[[^\]]*\]\(([^)\s]+)")
HEADING_PATTERN: Final = re.compile(r"^(#{1,6})\s+\S")
FENCE_PATTERN: Final = re.compile(r"^\s*```")
INLINE_CODE_PATTERN: Final = re.compile(r"`([^`\n]+)`")
PATHLIKE_PATTERN: Final = re.compile(r"/|\.(py|md|toml|lock|cfg|yaml|yml|txt|env)\b")
MARKER_PATTERN: Final = re.compile(r"\b(TODO|TBD|FIXME|XXX)\b")
QUALIFIED_INTERFACES_PATTERN: Final = re.compile(r"core/interfaces")
TOP_LEVEL_PATTERN: Final = re.compile(r"top[- ]level", re.IGNORECASE)
AMBIGUOUS_INTERFACES_SPANS: Final = frozenset({"interfaces", "interfaces/"})
SKILL_NAME_PATTERN: Final = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Fields defined by the Agent Skills specification. Anything else is a
# client-specific extension: portable, because clients ignore what they do not
# know, but worth reporting so the choice stays deliberate.
SPEC_FIELDS: Final = frozenset(
    {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
)

HEDGE_PHRASES: Final = (
    "as appropriate",
    "where appropriate",
    "where possible",
    "if possible",
    "best practice",
    "clean code",
    "as needed",
    "if needed",
    "try to",
    "generally",
    "usually",
    "ideally",
    "make sure to",
    "when in doubt",
    "and so on",
    "should probably",
    "as much as possible",
)

CLAIM_PATTERNS: Final = {
    "coverage 90%": re.compile(r"\b90\s?%"),
    "python 3.12": re.compile(r"\b3\.12\b|\bpy312\b"),
    "poetry": re.compile(r"\bpoetry\b", re.IGNORECASE),
    "ruff": re.compile(r"\bruff\b", re.IGNORECASE),
    "mypy strict": re.compile(r"mypy --strict|strict\s*=\s*true", re.IGNORECASE),
    "pytest": re.compile(r"\bpytest\b"),
    "requirements.txt": re.compile(r"requirements(-dev)?\.txt"),
    "black or isort": re.compile(r"\b(black|isort)\b", re.IGNORECASE),
    "pip install": re.compile(r"\bpip install\b", re.IGNORECASE),
    "change tiers": re.compile(r"\btier\s?[123]\b", re.IGNORECASE),
    "dependency rule": re.compile(r"\bcore/\b"),
}


@dataclass
class DocReport:
    """Measurements for a single markdown doc.

    Attributes:
        path: Doc path relative to the repo root, with forward slashes.
        lines: Total line count.
        words: Whitespace-delimited word count.
        headings: Heading count at any level.
        max_heading_depth: Deepest heading level present, 0 when there are none.
        code_blocks: Number of fenced code blocks.
        table_rows: Number of markdown table rows.
        path_anchors: Inline code spans that name a path, file, or command.
        links: Relative links found, as written.
        unresolved_links: Relative links whose target does not exist.
        hedge_hits: Hedge phrase occurrences as ``(line number, phrase)``.
        markers: Unresolved-work markers as ``(line number, marker)``.
        bare_interfaces: Lines referring to a directory as a bare ``interfaces``.
        reachable: Whether the entrypoint reaches this doc through links.
        is_skill: Whether this doc is a ``SKILL.md`` entrypoint.
        spec_issues: Agent Skills specification violations, for a ``SKILL.md``.
    """

    path: str
    lines: int
    words: int
    headings: int
    max_heading_depth: int
    code_blocks: int
    table_rows: int
    path_anchors: int
    links: list[str] = field(default_factory=list)
    unresolved_links: list[str] = field(default_factory=list)
    hedge_hits: list[tuple[int, str]] = field(default_factory=list)
    markers: list[tuple[int, str]] = field(default_factory=list)
    bare_interfaces: list[int] = field(default_factory=list)
    reachable: bool = False
    is_skill: bool = False
    spec_issues: list[str] = field(default_factory=list)


class AuditResult(TypedDict):
    """Envelope returned by :func:`audit`.

    Attributes:
        root: Repo root, as a POSIX path.
        entrypoint: Entrypoint filename, or None when it is absent.
        docs: One report per doc, in the order they were scanned.
        orphans: Paths not reachable from the entrypoint.
        unresolved_links: Unresolved link targets, keyed by doc path.
        spec_issues: Specification violations, keyed by ``SKILL.md`` path.
        client_extensions: Non-specification frontmatter, keyed by doc path.
        skills: Paths of the ``SKILL.md`` entrypoints.
        claim_spread: Docs asserting each load-bearing claim, keyed by claim.
    """

    root: str
    entrypoint: str | None
    docs: list[DocReport]
    orphans: list[str]
    unresolved_links: dict[str, list[str]]
    spec_issues: dict[str, list[str]]
    client_extensions: dict[str, list[str]]
    skills: list[str]
    claim_spread: dict[str, list[str]]


def _frontmatter(text: str) -> dict[str, str] | None:
    """Parse the top-level keys of a YAML frontmatter block.

    Only top-level ``key: value`` pairs are read, which is all the specification
    requires for validation. Nested mappings such as ``metadata`` are recorded as
    present with an empty value.

    Args:
        text: Full doc text.

    Returns:
        The top-level keys, or None when the doc has no frontmatter block.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if line[:1].isspace() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return None


def _spec_issues(path: Path, fields: dict[str, str] | None) -> list[str]:
    """Check a SKILL.md against the Agent Skills specification.

    Args:
        path: Absolute path to the ``SKILL.md`` file.
        fields: Parsed frontmatter, or None when the block is missing or unclosed.

    Returns:
        One message per violation; empty when the skill conforms.
    """
    if fields is None:
        return ["no closed YAML frontmatter block"]

    issues: list[str] = []
    name = fields.get("name", "")
    description = fields.get("description", "")
    expected = path.parent.name

    if not name:
        issues.append("missing required field: name")
    else:
        if not SKILL_NAME_PATTERN.fullmatch(name):
            issues.append(
                f"name {name!r} must be lowercase alphanumeric with single hyphens"
            )
        if len(name) > 64:
            issues.append(f"name is {len(name)} characters, over the 64 limit")
        if name != expected:
            issues.append(f"name {name!r} does not match parent directory {expected!r}")

    if not description:
        issues.append("missing required field: description")
    elif len(description) > 1024:
        issues.append(
            f"description is {len(description)} characters, over the 1024 limit"
        )

    return issues


def _is_bare_interfaces(line: str) -> bool:
    """Detect a directory reference to ``interfaces`` carrying no path qualifier.

    An inline code span of ``interfaces`` or ``interfaces/`` counts, because the
    trailing slash does not say which of the two directories is meant. A longer
    subpath such as ``interfaces/api/`` does say, and so does naming
    ``core/interfaces`` or the words "top level" on the same line. Ordinary
    English plurals are not backticked, and a heading about the ambiguity itself
    is expected rather than a defect, so both are excluded.

    Args:
        line: One line of markdown, outside a fenced code block.

    Returns:
        True when the line refers to either directory by the bare word.
    """
    if line.lstrip().startswith("#"):
        return False
    if QUALIFIED_INTERFACES_PATTERN.search(line) or TOP_LEVEL_PATTERN.search(line):
        return False
    return any(
        span.strip() in AMBIGUOUS_INTERFACES_SPANS
        for span in INLINE_CODE_PATTERN.findall(line)
    )


def _relative_links(text: str, source: Path, root: Path) -> tuple[list[str], list[str]]:
    """Extract relative markdown links and the subset that does not resolve.

    Args:
        text: Full doc text.
        source: Absolute path of the doc containing the links.
        root: Repo root, used to reject links escaping the repo.

    Returns:
        The relative links as written, and those whose target is missing.
    """
    links: list[str] = []
    unresolved: list[str] = []
    for target in LINK_PATTERN.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links.append(target)
        resolved = (source.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists() or root not in resolved.parents:
            unresolved.append(target)
    return links, unresolved


def _scan(path: Path, root: Path) -> DocReport:
    """Measure one doc.

    Args:
        path: Absolute path to the doc.
        root: Repo root.

    Returns:
        The doc's measurements.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    links, unresolved = _relative_links(text, path, root)

    heading_levels = [
        len(m.group(1)) for line in lines if (m := HEADING_PATTERN.match(line))
    ]
    anchors = sum(
        1
        for line in lines
        for span in INLINE_CODE_PATTERN.findall(line)
        if PATHLIKE_PATTERN.search(span)
    )

    hedges: list[tuple[int, str]] = []
    markers: list[tuple[int, str]] = []
    bare: list[int] = []
    in_fence = False
    for number, line in enumerate(lines, start=1):
        if FENCE_PATTERN.match(line):
            in_fence = not in_fence
        lowered = line.lower()
        hedges.extend((number, phrase) for phrase in HEDGE_PHRASES if phrase in lowered)
        markers.extend((number, m.group(1)) for m in MARKER_PATTERN.finditer(line))
        if not in_fence and _is_bare_interfaces(line):
            bare.append(number)

    is_skill = path.name == "SKILL.md"
    return DocReport(
        path=path.relative_to(root).as_posix(),
        lines=len(lines),
        words=len(text.split()),
        headings=len(heading_levels),
        max_heading_depth=max(heading_levels, default=0),
        code_blocks=sum(1 for line in lines if FENCE_PATTERN.match(line)) // 2,
        table_rows=sum(1 for line in lines if line.lstrip().startswith("|")),
        path_anchors=anchors,
        links=links,
        unresolved_links=unresolved,
        hedge_hits=hedges,
        markers=markers,
        bare_interfaces=bare,
        is_skill=is_skill,
        spec_issues=_spec_issues(path, _frontmatter(text)) if is_skill else [],
    )


def _reachable_from(seeds: list[Path], root: Path) -> set[str]:
    """Walk relative links outward from every entrypoint.

    Each ``SKILL.md`` is a seed as well as ``AGENTS.md``, because a client
    discovers skills directly and does not need a link to reach one. A reference
    file, by contrast, is only in play if its own skill points at it.

    Args:
        seeds: Docs an agent can reach without following a link.
        root: Repo root.

    Returns:
        Repo-relative posix paths of every markdown doc the walk reaches.
    """
    seen: set[str] = set()
    queue: deque[Path] = deque(seeds)
    while queue:
        current = queue.popleft()
        key = current.relative_to(root).as_posix()
        if key in seen or not current.exists():
            continue
        seen.add(key)
        links, _ = _relative_links(current.read_text(encoding="utf-8"), current, root)
        for target in links:
            resolved = (current.parent / target.split("#", 1)[0]).resolve()
            if resolved.suffix == ".md" and resolved.exists():
                queue.append(resolved)
    return seen


def audit(root: Path, docs_dir: str, entrypoint_name: str) -> AuditResult:
    """Audit every doc under ``docs_dir`` plus the entrypoint.

    Args:
        root: Repo root.
        docs_dir: Directory holding the instruction docs, relative to ``root``.
        entrypoint_name: Filename of the always-loaded entrypoint doc.

    Returns:
        Per-doc reports, orphan docs, unresolved links, and claim spread.

    Raises:
        FileNotFoundError: If ``docs_dir`` does not exist under ``root``.
    """
    docs_root = root / docs_dir
    if not docs_root.is_dir():
        raise FileNotFoundError(f"no {docs_dir}/ directory under {root}")

    entrypoint = root / entrypoint_name
    paths = sorted(docs_root.rglob("*.md"))

    seeds = [p for p in paths if p.name == "SKILL.md"]
    if entrypoint.exists():
        seeds.insert(0, entrypoint)
        paths.insert(0, entrypoint)
    reachable = _reachable_from(seeds, root)

    reports: list[DocReport] = []
    extensions: dict[str, list[str]] = {}
    claims: dict[str, list[str]] = {name: [] for name in CLAIM_PATTERNS}
    for path in paths:
        report = _scan(path, root)
        report.reachable = report.path in reachable
        if report.is_skill:
            fields = _frontmatter(path.read_text(encoding="utf-8")) or {}
            if found := sorted(set(fields) - SPEC_FIELDS):
                extensions[report.path] = found
        reports.append(report)
        text = path.read_text(encoding="utf-8")
        for name, pattern in CLAIM_PATTERNS.items():
            if pattern.search(text):
                claims[name].append(report.path)

    return {
        "root": root.as_posix(),
        "entrypoint": entrypoint_name if entrypoint.exists() else None,
        "docs": reports,
        "orphans": [r.path for r in reports if not r.reachable],
        "unresolved_links": {
            r.path: r.unresolved_links for r in reports if r.unresolved_links
        },
        "spec_issues": {r.path: r.spec_issues for r in reports if r.spec_issues},
        "client_extensions": extensions,
        "skills": [r.path for r in reports if r.is_skill],
        "claim_spread": {name: docs for name, docs in claims.items() if docs},
    }


def _render_text(result: AuditResult) -> str:
    """Render an audit result for reading in a terminal.

    Args:
        result: Value returned by :func:`audit`.

    Returns:
        The formatted report.
    """
    docs = result["docs"]
    skills = result["skills"]
    out: list[str] = [
        f"{len(docs)} docs audited under {result['root']}, "
        f"{len(skills)} of them skills",
        "",
    ]

    out.append(
        f"{'doc':44} {'lines':>5} {'words':>6} {'hdg':>4} {'code':>4} "
        f"{'tbl':>4} {'path':>5} {'link':>5}"
    )
    for doc in docs:
        flags = "".join(
            (
                "" if doc.reachable else "O",
                "L" if doc.unresolved_links else "",
                "H" if doc.hedge_hits else "",
                "M" if doc.markers else "",
                "I" if doc.bare_interfaces else "",
            )
        )
        out.append(
            f"{doc.path:44} {doc.lines:>5} {doc.words:>6} {doc.headings:>4} "
            f"{doc.code_blocks:>4} {doc.table_rows:>4} {doc.path_anchors:>5} "
            f"{len(doc.links):>5}  {flags}"
        )
    out += [
        "",
        "Flags: O orphan, L unresolved link, H hedge phrase, "
        "M TODO marker, I bare 'interfaces'",
        "",
    ]

    if result["orphans"]:
        out += ["Orphans (not reachable from the entrypoint):"]
        out += [f"  {path}" for path in result["orphans"]] + [""]

    if result["spec_issues"]:
        out += ["Agent Skills specification issues:"]
        for path, issues in result["spec_issues"].items():
            out += [f"  {path}:"] + [f"    - {issue}" for issue in issues]
        out.append("")
    else:
        out += [f"All {len(skills)} SKILL.md files conform to the specification.", ""]

    if result["client_extensions"]:
        out += [
            "Non-specification frontmatter, ignored by clients that do not support it:"
        ]
        for path, found in result["client_extensions"].items():
            out += [f"  {path}: {', '.join(found)}"]
        out.append("")

    if result["unresolved_links"]:
        out += ["Unresolved links:"]
        for path, targets in result["unresolved_links"].items():
            out += [f"  {path}: {', '.join(targets)}"]
        out.append("")

    hedged = [(doc.path, doc.hedge_hits) for doc in docs if doc.hedge_hits]
    if hedged:
        out += ["Hedge phrases (judge each; some are deliberate):"]
        for path, hits in hedged:
            joined = ", ".join(f'L{number} "{phrase}"' for number, phrase in hits)
            out += [f"  {path}: {joined}"]
        out.append("")

    unqualified = [
        (doc.path, doc.bare_interfaces) for doc in docs if doc.bare_interfaces
    ]
    if unqualified:
        out += ["Unqualified `interfaces` directory references:"]
        out += [
            f"  {path}: lines {', '.join(str(n) for n in numbers)}"
            for path, numbers in unqualified
        ]
        out.append("")

    markers = [(doc.path, doc.markers) for doc in docs if doc.markers]
    if markers:
        out += ["Unresolved-work markers:"]
        for path, hits in markers:
            out += [f"  {path}: {', '.join(f'L{n} {m}' for n, m in hits)}"]
        out.append("")

    out += ["Load-bearing claims by doc (compare these for contradictions):"]
    for name, paths in result["claim_spread"].items():
        out += [f"  {name}: {', '.join(paths)}"]

    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and print the audit.

    Args:
        argv: Argument vector, defaulting to ``sys.argv[1:]``.

    Returns:
        Process exit code. Non-zero under ``--strict`` when an orphan or an
        unresolved link was found.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(), help="repo root (default: cwd)"
    )
    parser.add_argument(
        "--docs-dir",
        default=".agents/skills",
        help="skills root (default: .agents/skills)",
    )
    parser.add_argument("--entrypoint", default="AGENTS.md", help="always-loaded doc")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 on orphans, dead links, or specification violations",
    )
    args = parser.parse_args(argv)

    try:
        result = audit(args.root.resolve(), args.docs_dir, args.entrypoint)
    except FileNotFoundError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    if args.format == "json":
        payload = {**result, "docs": [asdict(doc) for doc in result["docs"]]}
        print(json.dumps(payload, indent=2))
    else:
        print(_render_text(result))

    blocking = result["orphans"] or result["unresolved_links"] or result["spec_issues"]
    if args.strict and blocking:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
