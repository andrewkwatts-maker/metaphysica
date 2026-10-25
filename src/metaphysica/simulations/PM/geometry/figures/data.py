"""Reads the engine once and hands plain dicts to the pure figure functions."""
from typing import Any, Dict


def figure_data() -> Dict[str, Any]:
    """Engine data on the active path. `refusal` is None on the Joyce family,
    else the engine's own reason; resolution numbers exist only when it is None."""
    from metaphysica.simulations.PM.geometry.b3_path import resolve_path, seed_values
    from metaphysica.simulations.PM.geometry.g2_closure import (
        _resolution, closure_report)

    seed = resolve_path()
    b3, b2 = seed_values(seed)
    data: Dict[str, Any] = {
        "seed": seed, "declared_b2": b2, "declared_b3": b3,
        "closure": closure_report(), "resolution": None, "refusal": None}
    try:
        data["resolution"] = _resolution()
    except Exception as exc:  # the engine's refusal, shown verbatim
        data["refusal"] = "%s: %s" % (type(exc).__name__, exc)
    return data
