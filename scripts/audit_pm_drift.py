"""Diff PrincipiaMetaphysica's simulations/PM/ tree against this lib's copy.

Reports any algorithm-level differences. Ignores three known kinds of drift:

1. Import-prefix rewrites:
       from simulations.X   ->   from metaphysica.simulations.X
       import simulations.X ->   import metaphysica.simulations.X
2. Whitespace-only differences (blank lines, trailing spaces).
3. Files that exist on one side but not the other (reported separately).

Usage:
    python scripts/audit_pm_drift.py [--repo h:/Github/PrincipiaMetaphysica]

Output:
    A summary table + a JSON report at scripts/_audit_pm_drift.json (gitignored).

Exit code:
    0  if drift is import-prefix / whitespace only.
    1  if any file has algorithm-level drift (manual port needed).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

_LIB_ROOT = Path(__file__).resolve().parent.parent / "src" / "metaphysica" / "simulations" / "PM"
_DEFAULT_REPO = Path("h:/Github/PrincipiaMetaphysica/simulations/PM")

_IMPORT_REWRITES = [
    (re.compile(r"^(\s*)from\s+simulations\."), r"\1from metaphysica.simulations."),
    (re.compile(r"^(\s*)import\s+simulations\."), r"\1import metaphysica.simulations."),
    (re.compile(r"^(\s*)from\s+simulations\s"), r"\1from metaphysica.simulations "),
    (re.compile(r"^(\s*)import\s+simulations\s"), r"\1import metaphysica.simulations "),
]


@dataclass
class FileVerdict:
    relpath: str
    status: str  # "match" | "import_only" | "algo_drift" | "only_in_repo" | "only_in_lib"
    diff_preview: str = ""


@dataclass
class Report:
    files_compared: int = 0
    match: list[str] = field(default_factory=list)
    import_only: list[str] = field(default_factory=list)
    algo_drift: list[FileVerdict] = field(default_factory=list)
    only_in_repo: list[str] = field(default_factory=list)
    only_in_lib: list[str] = field(default_factory=list)


def _normalize(line: str) -> str:
    s = line.rstrip()
    for pat, repl in _IMPORT_REWRITES:
        m = pat.match(s)
        if m:
            s = pat.sub(repl, s)
            break
    return s


def _iter_py(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        yield p


def _compare(repo_file: Path, lib_file: Path) -> tuple[str, str]:
    """Return (status, diff_preview)."""
    repo_lines = [_normalize(l) for l in repo_file.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    lib_lines = [_normalize(l) for l in lib_file.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
    if repo_lines == lib_lines:
        # Were the raw bytes identical, or only equal post-normalization?
        raw_repo = repo_file.read_text(encoding="utf-8", errors="replace")
        raw_lib = lib_file.read_text(encoding="utf-8", errors="replace")
        if raw_repo == raw_lib:
            return "match", ""
        return "import_only", ""
    diff = list(difflib.unified_diff(repo_lines, lib_lines, lineterm="", n=2,
                                     fromfile=str(repo_file), tofile=str(lib_file)))
    preview = "\n".join(diff[:40])
    return "algo_drift", preview


def audit(repo_pm: Path, lib_pm: Path) -> Report:
    report = Report()
    repo_files = {p.relative_to(repo_pm).as_posix(): p for p in _iter_py(repo_pm)}
    lib_files = {p.relative_to(lib_pm).as_posix(): p for p in _iter_py(lib_pm)}

    for rel in sorted(set(repo_files) | set(lib_files)):
        report.files_compared += 1
        in_repo = rel in repo_files
        in_lib = rel in lib_files
        if in_repo and not in_lib:
            report.only_in_repo.append(rel)
            continue
        if in_lib and not in_repo:
            report.only_in_lib.append(rel)
            continue
        status, preview = _compare(repo_files[rel], lib_files[rel])
        if status == "match":
            report.match.append(rel)
        elif status == "import_only":
            report.import_only.append(rel)
        else:
            report.algo_drift.append(FileVerdict(rel, status, preview))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PM-tree drift audit")
    parser.add_argument("--repo", type=Path, default=_DEFAULT_REPO,
                        help="Path to PrincipiaMetaphysica/simulations/PM")
    parser.add_argument("--lib", type=Path, default=_LIB_ROOT,
                        help="Path to this lib's simulations/PM")
    parser.add_argument("--json", type=Path,
                        default=Path(__file__).resolve().parent / "_audit_pm_drift.json")
    args = parser.parse_args(argv)

    if not args.repo.exists():
        print(f"ERROR: repo PM tree not found at {args.repo}", file=sys.stderr)
        return 2
    if not args.lib.exists():
        print(f"ERROR: lib PM tree not found at {args.lib}", file=sys.stderr)
        return 2

    report = audit(args.repo, args.lib)

    print(f"Compared {report.files_compared} files")
    print(f"  match            {len(report.match):4d}")
    print(f"  import_only      {len(report.import_only):4d}")
    print(f"  ALGO_DRIFT       {len(report.algo_drift):4d}")
    print(f"  only_in_repo     {len(report.only_in_repo):4d}")
    print(f"  only_in_lib      {len(report.only_in_lib):4d}")

    if report.algo_drift:
        print("\n=== ALGORITHM-LEVEL DRIFT (manual port required) ===")
        for v in report.algo_drift:
            print(f"  {v.relpath}")
        print(f"\n(diff previews in {args.json})")

    if report.only_in_repo:
        print("\n=== ONLY IN REPO (port these into the lib) ===")
        for r in report.only_in_repo:
            print(f"  {r}")

    if report.only_in_lib:
        print("\n=== ONLY IN LIB (lib is ahead — no action) ===")
        for r in report.only_in_lib[:50]:
            print(f"  {r}")
        if len(report.only_in_lib) > 50:
            print(f"  ... and {len(report.only_in_lib)-50} more")

    payload = {
        "files_compared": report.files_compared,
        "match": report.match,
        "import_only": report.import_only,
        "algo_drift": [{"relpath": v.relpath, "preview": v.diff_preview} for v in report.algo_drift],
        "only_in_repo": report.only_in_repo,
        "only_in_lib": report.only_in_lib,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nReport written to {args.json}")

    return 1 if report.algo_drift else 0


if __name__ == "__main__":
    sys.exit(main())
