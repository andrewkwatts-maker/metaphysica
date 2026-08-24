#!/usr/bin/env python3
"""Strategy C: Structural — assert internal consistency of certificate JSON.

Each certificate is checked for self-consistency of its recorded fields:
the hash is non-empty hex, required fields are present and typed, the
gate_id is in [1, 72], the formula and wl_code are non-empty strings,
timestamp is parseable ISO-8601, the result field is non-empty.

This strategy does NOT check whether the stated formula is physically correct;
it only checks that the certificate record is internally coherent and that
enough information is present for a human or future tool to evaluate it.

SAMPLE: 6 of the 24 DECLARATIVE gates are converted here.
    G01 — Integer Root Parity
    G12 — Electroweak Alignment
    G22 — Gluon String Tension
    G29 — Weak Hypercharge
    G36 — CKM Matrix Unitarity
    G37 — CP-Violation Phase

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "ConsistencyCheck",
    "StructuralCheckResult",
    "check_gate",
    "run_all",
]

# Required fields and their expected Python types.
_REQUIRED_FIELDS: Dict[str, type] = {
    "proof_id": str,
    "gate_id": int,
    "gate_name": str,
    "formula": str,
    "wl_code": str,
    "result": str,
    "verification_status": str,
    "evaluation_status": str,
    "hash": str,
    "timestamp": str,
}

_HEX_RE = re.compile(r"^[0-9a-fA-F]+$")
_ISO_STRICT = "%Y-%m-%dT%H:%M:%S"   # may have fractional seconds / Z suffix


@dataclass
class ConsistencyCheck:
    field_name: str
    passed: bool
    detail: str


@dataclass
class StructuralCheckResult:
    gate_id: int
    gate_name: str
    verdict: str                       # "PASS" | "FAIL"
    checks: List[ConsistencyCheck] = field(default_factory=list)
    numbers_invented: int = 0          # always 0 for structural checks
    note: str = ""

    @property
    def failures(self) -> List[ConsistencyCheck]:
        return [c for c in self.checks if not c.passed]


def _certs_dir() -> Path:
    from metaphysica.generators._common import autogen_dir
    return autogen_dir() / "certificates"


def _load_cert(gate_id: int) -> Optional[Dict[str, Any]]:
    certs_dir = _certs_dir()
    # Certificates are named G##_<snake_name>.json
    for path in certs_dir.glob(f"G{gate_id:02d}_*.json"):
        with open(path) as fh:
            return json.load(fh)
    return None


def _run_checks(cert: Dict[str, Any]) -> List[ConsistencyCheck]:
    checks: List[ConsistencyCheck] = []

    # 1. Required fields present and correct type
    for fname, ftype in _REQUIRED_FIELDS.items():
        val = cert.get(fname)
        if val is None:
            checks.append(ConsistencyCheck(fname, False, f"field missing"))
        elif not isinstance(val, ftype):
            checks.append(ConsistencyCheck(
                fname, False,
                f"expected {ftype.__name__}, got {type(val).__name__}: {val!r}"
            ))
        else:
            checks.append(ConsistencyCheck(fname, True, f"present, type {ftype.__name__}"))

    # 2. gate_id in valid range [1, 72]
    gid = cert.get("gate_id")
    if isinstance(gid, int):
        ok = 1 <= gid <= 72
        checks.append(ConsistencyCheck(
            "gate_id_range", ok,
            f"gate_id={gid} {'in' if ok else 'outside'} [1,72]"
        ))

    # 3. hash is non-empty hex string
    h = cert.get("hash", "")
    if isinstance(h, str) and h:
        ok = bool(_HEX_RE.match(h))
        checks.append(ConsistencyCheck(
            "hash_is_hex", ok,
            f"hash={h!r} {'is hex' if ok else 'is NOT hex'}"
        ))
    else:
        checks.append(ConsistencyCheck("hash_is_hex", False, "hash empty or missing"))

    # 4. timestamp parseable
    ts = cert.get("timestamp", "")
    if isinstance(ts, str) and ts:
        try:
            # strip trailing Z, fractional seconds for parsing
            ts_clean = ts.rstrip("Z").split(".")[0]
            datetime.strptime(ts_clean, _ISO_STRICT)
            checks.append(ConsistencyCheck("timestamp_parseable", True, f"parsed OK"))
        except ValueError as exc:
            checks.append(ConsistencyCheck(
                "timestamp_parseable", False, f"cannot parse '{ts}': {exc}"
            ))
    else:
        checks.append(ConsistencyCheck("timestamp_parseable", False, "timestamp missing"))

    # 5. evaluation_status matches expected set
    ev_status = cert.get("evaluation_status", "")
    valid_statuses = {"COMPUTED_PASS", "COMPUTED_FAIL", "DECLARATIVE", "COMPUTED_INFO"}
    ok = ev_status in valid_statuses
    checks.append(ConsistencyCheck(
        "evaluation_status_valid", ok,
        f"'{ev_status}' {'valid' if ok else 'UNKNOWN'}"
    ))

    # 6. formula and wl_code are non-empty
    for fname in ("formula", "wl_code"):
        val = cert.get(fname, "")
        ok = isinstance(val, str) and val.strip() != ""
        checks.append(ConsistencyCheck(
            f"{fname}_nonempty", ok,
            f"{'non-empty' if ok else 'EMPTY'}"
        ))

    # 7. result field is non-empty
    result_val = cert.get("result", "")
    ok = isinstance(result_val, str) and result_val.strip() != ""
    checks.append(ConsistencyCheck(
        "result_nonempty", ok,
        f"{'non-empty' if ok else 'EMPTY'}"
    ))

    # 8. evaluation sub-object present and has 'tier' and 'status' keys
    ev = cert.get("evaluation", {})
    if isinstance(ev, dict):
        ok = ("tier" in ev) and ("status" in ev)
        checks.append(ConsistencyCheck(
            "evaluation_subobject", ok,
            f"{'has tier+status' if ok else 'missing tier or status'}"
        ))
    else:
        checks.append(ConsistencyCheck("evaluation_subobject", False, "evaluation not a dict"))

    return checks


def check_gate(gate_id: int) -> StructuralCheckResult:
    cert = _load_cert(gate_id)
    if cert is None:
        return StructuralCheckResult(
            gate_id=gate_id,
            gate_name="UNKNOWN",
            verdict="FAIL",
            checks=[ConsistencyCheck("cert_file", False, f"G{gate_id:02d} certificate file not found")],
            note="Certificate file missing from AutoGenerated/certificates/",
        )

    gate_name = cert.get("gate_name", f"G{gate_id:02d}")
    checks = _run_checks(cert)
    n_fail = sum(1 for c in checks if not c.passed)
    verdict = "PASS" if n_fail == 0 else "FAIL"
    return StructuralCheckResult(
        gate_id=gate_id,
        gate_name=gate_name,
        verdict=verdict,
        checks=checks,
        numbers_invented=0,
        note=f"{len(checks)} checks, {n_fail} failures",
    )


# Sample: 6 gates
_SAMPLE_GATE_IDS = [1, 12, 22, 29, 36, 37]


def run_all() -> List[StructuralCheckResult]:
    return [check_gate(gid) for gid in _SAMPLE_GATE_IDS]


def main() -> int:
    results = run_all()
    print("=" * 60)
    print(" STRATEGY C — STRUCTURAL CONSISTENCY CHECKS")
    print("=" * 60)
    n_pass = sum(1 for r in results if r.verdict == "PASS")
    for r in results:
        print(f"  [{r.verdict}] G{r.gate_id:02d} {r.gate_name}  ({r.note})")
        for c in r.failures:
            print(f"        FAIL: {c.field_name} — {c.detail}")
    print(f"\n  {n_pass}/{len(results)} PASS  |  0 numbers invented (structural only)")
    return 0 if n_pass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
