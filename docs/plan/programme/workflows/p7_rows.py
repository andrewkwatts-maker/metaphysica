"""P7 ledger tool: split the lane files by kind, check a merged ledger, count it.

    python p7_rows.py split  <ideas dir> <out dir>   rows_<kind>.md, timeline.md, eras.md,
                                                     candidates.md, gaps.md, unparsed.md
    python p7_rows.py forks  <out dir>               catalogue.md (needs PYTHONPATH=src)
    python p7_rows.py check  <ideas dir> <out dir> [kind]   lane rows no ledger row cites
    python p7_rows.py counts <ideas dir>             ledger rows by kind, fate, class, flag

Lane files are `<ideas dir>/<lane>.md`; ledgers are `<ideas dir>/ledger_<kind>.md`.
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

KINDS = ("bulk", "shadows", "time", "internal", "lattice", "topology-number", "generations",
         "action", "gauge", "particle", "cosmology", "identity", "other")
SECTIONS = {"1": "eras", "2": "timeline", "3": "ideas", "4": "candidates", "5": "gaps", "6": "gaps"}
ROW_HEAD = "| lane | id | idea | kind | first seen | last seen | fate | reason recorded | reason type | today |"
SOURCE_REF = re.compile(r"([a-z]+-[0-9a-z_-]+):\s*([A-Za-z0-9][A-Za-z0-9_.-]*)")


def cells(line: str) -> list[str]:
    """Cells of one table row; an escaped bar stays inside its cell."""
    body = line.strip().strip("|")
    return [c.strip().replace("\\|", "/") for c in re.split(r"(?<!\\)\|", body)]


def is_rule(parts: list[str]) -> bool:
    return all(set(p) <= set("-: ") for p in parts)


def lane_files(ideas: Path) -> list[Path]:
    return sorted(p for p in ideas.glob("*.md") if not p.name.startswith("ledger_"))


def sections(path: Path) -> dict[str, list[str]]:
    """Lines of a lane file under the name of the numbered section they sit in."""
    out: dict[str, list[str]] = collections.defaultdict(list)
    name = "head"
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"##\s+(\d)\.", line)
        if match:
            name = SECTIONS.get(match.group(1), "head")
            continue
        out[name].append(line)
    return out


def idea_rows(lane: str, lines: list[str]) -> tuple[list[list[str]], list[str]]:
    """Parsed idea rows (lane first) and the lines that do not parse as nine cells."""
    good, bad = [], []
    for line in lines:
        if not line.startswith("|"):
            continue
        parts = cells(line)
        if is_rule(parts) or parts[0].lower() == "id":
            continue
        if len(parts) != 9:
            bad.append(f"{lane}: {line}")
            continue
        good.append([lane, *parts])
    return good, bad


def kind_of(row: list[str]) -> str:
    word = row[3].lower().split()[0].strip(",;") if row[3] else ""
    return word if word in KINDS else "other"


def split(ideas: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    by_kind: dict[str, list[str]] = collections.defaultdict(list)
    loose: dict[str, list[str]] = collections.defaultdict(list)
    for path in lane_files(ideas):
        lane, parts = path.stem, sections(path)
        rows, bad = idea_rows(lane, parts["ideas"])
        loose["unparsed"] += bad
        for row in rows:
            by_kind[kind_of(row)].append("| " + " | ".join(row) + " |")
        for name in ("eras", "timeline", "candidates", "gaps"):
            loose[name] += [f"### {lane}", *[x for x in parts[name] if x.strip()], ""]
    for kind in KINDS:
        text = [f"# Lane rows of kind `{kind}` ({len(by_kind[kind])})", "", ROW_HEAD,
                "|" + "---|" * 10, *by_kind[kind]]
        (out / f"rows_{kind}.md").write_text("\n".join(text) + "\n", encoding="utf-8")
        print(f"{kind}: {len(by_kind[kind])}")
    for name, lines in loose.items():
        (out / f"{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"unparsed: {len(loose['unparsed'])}")
    return 0


def forks(out: Path) -> int:
    from metaphysica.simulations.core.variants.report import describe

    lines = ["# Forks and options in `simulations/core/variants` today", ""]
    for fork_id, fork in describe()["forks"].items():
        lines += [f"## {fork_id} (status {fork.get('status')}, default {fork.get('default')})",
                  f"{fork.get('question', '')}", "",
                  "| option | status | summary | consequence |", "|---|---|---|---|"]
        for opt in fork.get("options", []):
            text = [str(opt.get(k, "")).replace("|", "/").replace("\n", " ")
                    for k in ("id", "status", "summary", "consequence")]
            text[3] = text[3][:260]
            lines.append("| " + " | ".join(text) + " |")
        lines.append("")
    out.mkdir(parents=True, exist_ok=True)
    (out / "catalogue.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"forks: {sum(1 for x in lines if x.startswith('## '))}")
    return 0


def ledger_rows(ideas: Path, kind: str | None = None) -> list[tuple[str, list[str]]]:
    """(ledger kind, cells) for every idea row of the ledgers."""
    out = []
    for path in sorted(ideas.glob("ledger_*.md")):
        name = path.stem.removeprefix("ledger_")
        if name not in KINDS or (kind and name != kind):
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            parts = cells(line) if line.startswith("|") else []
            if parts and re.match(r"I-[A-Z]+-\d+", parts[0]):
                out.append((name, parts))
    return out


def check(ideas: Path, out: Path, kind: str | None = None) -> int:
    cited: collections.Counter = collections.Counter()
    width: collections.Counter = collections.Counter()
    for _, parts in ledger_rows(ideas, kind):
        width[len(parts)] += 1
        for lane, row_id in SOURCE_REF.findall(parts[7] if len(parts) > 7 else ""):
            cited[(lane, row_id)] += 1
    missing = []
    for name in ([kind] if kind else KINDS):
        for line in (out / f"rows_{name}.md").read_text(encoding="utf-8").splitlines():
            parts = cells(line) if line.startswith("|") else []
            if len(parts) == 10 and parts[0] != "lane" and not is_rule(parts):
                if not cited[(parts[0], parts[1])]:
                    missing.append(f"{name}: {parts[0]}:{parts[1]}")
    twice = [f"{lane}:{row_id} x{n}" for (lane, row_id), n in cited.items() if n > 1]
    print(f"ledger rows by cell count: {dict(width)} (11 expected)")
    print(f"lane rows with no ledger row: {len(missing)}")
    print("\n".join(missing[:80]))
    print(f"lane rows cited by more than one ledger row: {len(twice)}")
    print("; ".join(twice[:40]))
    return 1 if missing or set(width) - {11} else 0


def counts(ideas: Path) -> int:
    tallies = {name: collections.Counter() for name in ("kind", "fate", "class", "re-evaluate")}
    for kind, parts in ledger_rows(ideas):
        if len(parts) != 11:
            continue
        tallies["kind"][kind] += 1
        tallies["fate"][parts[4].split()[0]] += 1
        tallies["class"][parts[8][:1]] += 1
        tallies["re-evaluate"][parts[9][:2]] += 1
    for name, tally in tallies.items():
        print(name + ": " + ", ".join(f"{k} {v}" for k, v in sorted(tally.items())))
    print(f"total: {sum(tallies['kind'].values())}")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    command, rest = argv[0], [Path(a) for a in argv[1:3]]
    if command == "split" and len(rest) == 2:
        return split(*rest)
    if command == "forks":
        return forks(rest[0])
    if command == "check" and len(rest) == 2:
        return check(rest[0], rest[1], argv[3] if len(argv) > 3 else None)
    if command == "counts":
        return counts(rest[0])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
