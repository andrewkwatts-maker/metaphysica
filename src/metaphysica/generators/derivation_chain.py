"""One rule for a parameter's derivation chain: its declared formula's inputs.

Shared by the exporter (which records the chain on each registry row) and the
parameter ledger (which walks chains), so the rule is written once. A formula
that lists the parameter among its own inputs is a check, not a parent.
"""
from typing import Any, Dict, List, Optional


def formula_inputs(name: str, formula: Dict[str, Any]) -> List[str]:
    """Input params of *formula* other than *name* itself, in order, no repeats."""
    out: List[str] = []
    for i in formula.get("input_params") or []:
        if i != name and i not in out:
            out.append(i)
    return out


def declared_chain(name: str, fid: Optional[str], formulas: Dict[str, Any]) -> List[str]:
    """Chain for *name* from its declared formula *fid*; empty when none or unknown."""
    if not fid or fid not in formulas:
        return []
    return formula_inputs(name, formulas[fid])


def declared_formula_errors(params: Dict[str, Any], formulas: Dict[str, Any]) -> List[str]:
    """Declared derivation_formula links that fail: unknown id, or output not listed."""
    errors: List[str] = []
    for name, row in params.items():
        fid = row.get("derivation_formula") if isinstance(row, dict) else None
        if not fid:
            continue
        if fid not in formulas:
            errors.append("%s: unknown formula %s" % (name, fid))
        elif name not in (formulas[fid].get("output_params") or []):
            errors.append("%s: formula %s does not list it in output_params" % (name, fid))
    return errors
