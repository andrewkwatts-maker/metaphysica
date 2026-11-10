"""Every related_formulas / parent_formulas id in core_formulas.py resolves."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src/metaphysica/config/core_formulas.py"

#: Defined by other generators and registered at build time, not in CoreFormulas.
EXTERNAL_IDS = {"betti-numbers", "breathing-mode", "g2-holonomy"}
#: Pending: a separate lane defines the canonical master action under this id.
#: See docs/plan/MASTER_ACTION_SELECTION_2026-11-01.md.
PENDING_IDS = {"master-action-26d"}


def _ids_and_refs():
    text = SRC.read_text(encoding="utf-8")
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    refs = set()
    for m in re.finditer(r'(?:related|parent)_formulas=\[([^\]]*)\]', text):
        refs.update(re.findall(r'"([^"]+)"', m.group(1)))
    return ids, refs


def test_all_formula_references_resolve():
    ids, refs = _ids_and_refs()
    dangling = refs - ids - EXTERNAL_IDS - PENDING_IDS
    assert not dangling, f"dangling formula ids: {sorted(dangling)}"
