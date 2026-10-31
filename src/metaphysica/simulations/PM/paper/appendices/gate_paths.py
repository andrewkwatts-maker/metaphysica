"""Path-aware inputs and applicability for the Appendix F gates.

A gate reads the value the selected path gives, never a literal. A gate whose
premise the path does not carry is NOT_APPLICABLE rather than failed. Missing
inputs fail early and name the row.
"""
from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Tuple

PASS = "PASS"
FAIL = "FAIL"
NOT_APPLICABLE = "NOT_APPLICABLE"

# model_data key -> registry row (b3 is read through the fork-resolved path).
ROW_OF_KEY: Dict[str, str] = {
    "roots": "topology.ancestral_roots",
    "active": "registry.node_count",
    "torsion": "topology.shadow_torsion_total",
    "per_shadow": "topology.torsion_per_shadow",
}
B3_ROW = "b3_path.seed_values (fork b3_seed)"

# gate -> {fork: option the gate's premise needs}. Absent = premise carried by
# every path. G31 states v = k_gimel * (b3 - 4); the stated check only closes
# at b3 = 24, the seed_24 branch (see docs/plan/paths/hidden_forks.md, G1).
PREMISES: Dict[int, Dict[str, str]] = {
    31: {"b3_seed": "seed_24"},
}

# Gate -> model_data keys the gate reads (declared, then enforced).
READS: Dict[int, Tuple[str, ...]] = {
    6: ("torsion", "per_shadow"),
    9: ("torsion", "per_shadow"),
    12: ("torsion", "per_shadow"),
    22: ("torsion", "per_shadow", "roots"),
    29: ("torsion", "per_shadow"),
    31: ("b3",),
    63: ("torsion", "per_shadow"),
}


class MissingGateInput(KeyError):
    """A gate input the selected path did not publish."""


def need(model_data: Mapping[str, Any], key: str) -> Any:
    """model_data[key], or fail early naming the registry row."""
    if model_data.get(key) is None:
        row = B3_ROW if key == "b3" else ROW_OF_KEY.get(key, key)
        raise MissingGateInput(f"gate input '{key}' missing (row {row})")
    return model_data[key]


def read_inputs(registry: Any) -> Dict[str, Any]:
    """Gate inputs from the registry the selected path produced; no defaults."""
    from metaphysica.simulations.PM.geometry.b3_path import seed_values

    data: Dict[str, Any] = {}
    for key, row in ROW_OF_KEY.items():
        try:
            value = registry.get(row)
        except KeyError:
            value = None
        if value is None:
            raise MissingGateInput(f"gate input '{key}' missing (row {row})")
        data[key] = value
    data["hidden"] = data["roots"] - data["active"]
    data["b3"] = seed_values()[0]
    return data


def applicability(gate_id: int, selection: Mapping[str, str]) -> Tuple[bool, str]:
    """(applies, reason) for a gate on the selection in force."""
    for fork, option in PREMISES.get(gate_id, {}).items():
        chosen = selection.get(fork)
        if chosen != option:
            return False, f"premise needs {fork}={option}; path has {chosen}"
    return True, ""


def resolve_selection(model_data: Mapping[str, Any]) -> Dict[str, str]:
    """The selection in force: given in model_data, else the active one."""
    given: Optional[Dict[str, str]] = model_data.get("selection")  # type: ignore
    if given is not None:
        return dict(given)
    from metaphysica.simulations.core.variants import active_selection

    return active_selection()


def path_id(selection: Mapping[str, str]) -> str:
    """Digest of the selection, as the run directory and paths index name it."""
    from metaphysica.simulations.core.variants import selection_id

    return selection_id(dict(selection))
