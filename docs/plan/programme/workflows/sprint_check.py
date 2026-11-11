"""Check a sprint file: each step has what an executor needs and no file is owned twice.

Usage: python sprint_check.py <sprint.json> [<inflight.json>]

A sprint is {"sprint": name, "chains": [{"id", "title", "steps": [{"id", "target", "read",
"files", "test"}]}]}. Steps of one chain run in turn; chains run side by side, so a file may
belong to one chain only. The in-flight file is {"files": [...]}: files owned by lanes that are
running now; an entry ending in "/" covers everything under it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED = ("id", "target", "read", "files", "test")


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def in_flight(name: str, inflight: list[str]) -> bool:
    return any(name == entry or (entry.endswith("/") and name.startswith(entry)) for entry in inflight)


def step_problems(chain_id: str, step: dict, inflight: list[str]) -> list[str]:
    where = f"{chain_id}/{step.get('id', '?')}"
    found = [f"{where}: no {key}" for key in REQUIRED if not step.get(key)]
    found += [f"{where}: {name} is owned by a running lane"
              for name in step.get("files", []) if in_flight(name, inflight)]
    return found


def problems(sprint: dict, inflight: list[str]) -> list[str]:
    found: list[str] = []
    owner: dict[str, str] = {}
    seen: set[str] = set()
    for chain in sprint["chains"]:
        for step in chain["steps"]:
            found += step_problems(chain["id"], step, inflight)
            if step.get("id") in seen:
                found.append(f"{chain['id']}/{step.get('id')}: step id used twice")
            seen.add(step.get("id"))
            for name in step.get("files", []):
                first = owner.setdefault(name, chain["id"])
                if first != chain["id"]:
                    found.append(f"{name}: owned by chains {first} and {chain['id']}")
    return found


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    sprint = load(argv[1])
    inflight = load(argv[2])["files"] if len(argv) > 2 else []
    found = problems(sprint, inflight)
    steps = sum(len(chain["steps"]) for chain in sprint["chains"])
    print("\n".join(found) if found else f"ok: {len(sprint['chains'])} chains, {steps} steps")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
