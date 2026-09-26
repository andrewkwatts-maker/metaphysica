"""FormulasRegistry (SSoT) access for the config package.

Extracted verbatim from the former single-file ``config.py``; no values,
formulas or strings were changed by the move.
"""


# SSoT: FormulasRegistry provides the Ten Pillar Seeds and derived geometric constants.
# Import is optional here since config.py defines its own class-level constants for
# documentation purposes, but FormulasRegistry is the authoritative source.
# To enforce SSoT, simulations should use FormulasRegistry directly.
try:
    from metaphysica.simulations.core.FormulasRegistry import (
        FormulasRegistry,
        get_registry as _get_registry,
    )
    _REGISTRY_AVAILABLE = True
except ImportError:
    _REGISTRY_AVAILABLE = False


def _ssot_dim(prop: str) -> int:
    """Read one dimensional constant from FormulasRegistry, the SSOT.

    The dimensional integers used to be written here as literals, which made
    config.py a parallel store of values that live authoritatively in
    FormulasRegistry -- exactly the ORPHAN class generate_config_drift_audit.py
    exists to surface, and this module's own comment above concedes it is not
    authoritative.

    It matters beyond tidiness: CANON["D_bulk"] is STRUCTURAL_CHALLENGED while
    the (24,2)/26D vs (26,2)/28D ruling is open. A literal 26 here would have to
    be found and edited by hand the day that ruling lands; a registry read
    follows it.

    Deliberately no literal fallback. If the registry cannot be imported, the
    honest outcome is a loud failure -- a hardcoded default would silently
    reintroduce the drift this removes.
    """
    if not _REGISTRY_AVAILABLE:
        raise RuntimeError(
            f"config.py needs FormulasRegistry to resolve {prop!r}; it is the "
            "single source of truth for dimensional structure and there is no "
            "literal fallback by design."
        )
    return getattr(_get_registry(), prop)
