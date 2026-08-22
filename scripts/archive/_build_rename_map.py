"""Build a class-rename map (old -> new) by scanning PM modules for class
definitions whose name ends in V16, V17, V16_<n>, V17_<n>.

Writes JSON to _class_rename_map.json. Detects collisions (multiple olds -> same new)
and raises rather than silently merging.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

PM_ROOT = Path(r"H:\Github\metaphysica\src\metaphysica\simulations\PM")
OUT_PATH = Path(__file__).parent / "_class_rename_map.json"

# Match ` class Foo[V16|V17][_<digits>]*(` style class headers.
# Captures the full class name and the suffix to strip.
CLASS_RE = re.compile(
    r"^class\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*?)(?P<suffix>V1[67](?:_[0-9]+)*)\s*[\(:]",
    re.MULTILINE,
)


def main() -> None:
    rename_map: dict[str, str] = {}
    collisions: dict[str, list[str]] = {}
    per_file: dict[str, list[tuple[str, str]]] = {}

    for py in sorted(PM_ROOT.rglob("*.py")):
        try:
            text = py.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = py.read_text(encoding="utf-8", errors="replace")
        for m in CLASS_RE.finditer(text):
            base = m.group("name")
            suffix = m.group("suffix")
            old = base + suffix
            new = base
            if not new:
                # Edge: class _V16(...) — base is empty. Skip; unlikely.
                continue
            if old in rename_map and rename_map[old] != new:
                raise RuntimeError(f"Inconsistent map for {old}: {rename_map[old]} vs {new}")
            if new in collisions:
                collisions[new].append(old)
            else:
                # Check whether another already maps to this new
                existing = [o for o, n in rename_map.items() if n == new and o != old]
                if existing:
                    collisions[new] = existing + [old]
            rename_map[old] = new
            per_file.setdefault(str(py.relative_to(PM_ROOT)), []).append((old, new))

    # True collisions: more than one distinct old maps to the same new.
    real_collisions = {n: list(set(olds)) for n, olds in collisions.items() if len(set(olds)) > 1}

    out = {
        "rename_map": rename_map,
        "per_file": per_file,
        "collisions": real_collisions,
        "count": len(rename_map),
    }
    OUT_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} with {len(rename_map)} renames across {len(per_file)} files.")
    if real_collisions:
        print("\n*** COLLISIONS DETECTED ***")
        for new, olds in real_collisions.items():
            print(f"  {new}  <-  {olds}")
        raise SystemExit(2)
    print("\nFirst 10 renames:")
    for i, (k, v) in enumerate(rename_map.items()):
        if i >= 10:
            break
        print(f"  {k}  ->  {v}")


if __name__ == "__main__":
    main()
