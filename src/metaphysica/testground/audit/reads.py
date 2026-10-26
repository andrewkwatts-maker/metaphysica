"""Reconcile what was read with what the gates declare.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Mapping, Sequence, Tuple

from metaphysica.testground.audit.rows import Selection

__all__ = ["ReadFindings", "reconcile_reads"]

RunReads = Tuple[Selection, Mapping[str, int]]


@dataclass
class ReadFindings:
    never_read: List[str] = field(default_factory=list)
    undeclared_gates: List[Tuple[str, str]] = field(default_factory=list)
    closed_gate_reads: List[Tuple[str, str]] = field(default_factory=list)


def reconcile_reads(forks: Sequence[Any], runs: Mapping[str, RunReads], *,
                    gate_open: Callable[[str, Selection], bool] = lambda f, s: True
                    ) -> ReadFindings:
    """Forks never read; unread with the gate open; read with the gate closed."""
    found = ReadFindings()
    for fork in forks:
        fid = fork.id
        if not any(reads.get(fid, 0) for _, reads in runs.values()):
            found.never_read.append(fid)
        for run_id, (sel, reads) in runs.items():
            read, opened = reads.get(fid, 0) > 0, gate_open(fid, sel)
            if opened and not read:
                found.undeclared_gates.append((fid, run_id))
            elif read and not opened:
                found.closed_gate_reads.append((fid, run_id))
    found.never_read.sort()
    found.undeclared_gates.sort()
    found.closed_gate_reads.sort()
    return found
