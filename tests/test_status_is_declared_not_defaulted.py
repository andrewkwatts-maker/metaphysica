"""A status nobody declared must not be indistinguishable from one that was.

set_param used to default status to "DERIVED". Any caller that omitted it
published a derivation nobody claimed -- the laundering pattern at its source,
and unrecoverable after the fact because the row looked identical to a declared
derivation.

The default is now None. Behaviour is preserved (the effective status is still
DERIVED, so no published number moves) but the row records that its status was
DEFAULTED. These tests pin that distinction, and pin the count so it can only
go down.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from metaphysica.simulations.base.registry import PMRegistry


def _metadata(registry, path):
    row = registry._parameters[path]
    return getattr(row, "metadata", None) or {}


def test_a_declared_status_is_not_marked_defaulted():
    r = PMRegistry()
    r.set_param("t.declared", 1.0, source="s", status="GEOMETRIC")
    assert r._parameters["t.declared"].status == "GEOMETRIC"
    assert _metadata(r, "t.declared").get("status_defaulted") is not True


def test_an_omitted_status_still_works_but_is_marked():
    """Behaviour preserved, provenance recovered."""
    r = PMRegistry()
    r.set_param("t.defaulted", 2.0, source="s")
    assert r._parameters["t.defaulted"].status == "DERIVED", (
        "the effective status must stay DERIVED so nothing published moves"
    )
    md = _metadata(r, "t.defaulted")
    assert md.get("status_defaulted") is True
    assert "not a claim made by the simulation" in md["status_defaulted_note"]


def test_explicitly_passing_derived_is_a_claim_not_a_default():
    """Declaring DERIVED on purpose must remain distinguishable from silence."""
    r = PMRegistry()
    r.set_param("t.explicit", 3.0, source="s", status="DERIVED")
    assert r._parameters["t.explicit"].status == "DERIVED"
    assert _metadata(r, "t.explicit").get("status_defaulted") is not True


def test_caller_metadata_survives_the_marking():
    r = PMRegistry()
    r.set_param("t.meta", 4.0, source="s", metadata={"units": "GeV"})
    md = _metadata(r, "t.meta")
    assert md["units"] == "GeV"
    assert md["status_defaulted"] is True


def test_the_marking_does_not_mutate_the_callers_dict():
    r = PMRegistry()
    caller = {"units": "GeV"}
    r.set_param("t.nomutate", 5.0, source="s", metadata=caller)
    assert "status_defaulted" not in caller, (
        "set_param mutated the caller's metadata dict"
    )


# ------------------------------------------------- the count, so it can only fall


def _count_defaulted_call_sites() -> int:
    root = pathlib.Path(__file__).resolve().parents[1] / "src" / "metaphysica"
    total = 0
    for path in root.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name != "set_param":
                continue
            if "status" not in {k.arg for k in node.keywords if k.arg}:
                total += 1
    return total


#: Measured 2026-09-14. A ratchet: call sites that declare their status are
#: the goal, so this number may fall but must not rise.
DEFAULTED_CALL_SITES_BASELINE = 45


def test_defaulted_call_sites_do_not_increase():
    count = _count_defaulted_call_sites()
    assert count <= DEFAULTED_CALL_SITES_BASELINE, (
        "%d set_param calls now omit status, up from the %d baseline. A new "
        "call site is publishing a derivation nobody declared; pass an "
        "explicit status." % (count, DEFAULTED_CALL_SITES_BASELINE)
    )


def test_the_baseline_is_not_stale():
    """If the count has fallen, tighten the ratchet rather than leave slack."""
    count = _count_defaulted_call_sites()
    assert count >= DEFAULTED_CALL_SITES_BASELINE - 5, (
        "only %d call sites now omit status (baseline %d). Lower "
        "DEFAULTED_CALL_SITES_BASELINE so the ratchet keeps its grip."
        % (count, DEFAULTED_CALL_SITES_BASELINE)
    )
