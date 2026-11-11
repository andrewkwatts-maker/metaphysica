"""R2-21, R2-22: the FormulasRegistry symbol tables quote the path in force.

The close-out guard (test_path_core_closeout_seed_text.py) scans for seed-24
arithmetic written with ``*`` and checks the LATEX_REGISTRY trailing comments.
It did not see two shapes, both of which this file reads:

* multiplication written with a letter x or a times sign (``288 = 12 x b3``,
  ``24 x 12``): 12 x b3 is 288 only at the retired seed b3 = 24;
* comment table rows ``# <value> | <key> | ...``: the value in the first
  column is evaluated and compared with what the registry serves under the
  key the row names. A seed-24 number may stay in the row's text with a
  seed_24 label, never in the value column.

The typed ``value`` of each HEBREW_SYMBOL_REGISTRY entry is held to the same
rule, because get_latex_term serves it. R2-22: the claim that
pressure_divisor equals chi_eff_total holds at seed_24 only and says so.
"""
import importlib
import math
import re
from pathlib import Path

from metaphysica.simulations.core.variants import selection

fr = importlib.import_module("metaphysica.simulations.core.FormulasRegistry")

SOURCE = Path(fr.__file__).read_text(encoding="utf-8").splitlines()

#: The close-out alternatives, with every product also read when it is written
#: with a letter x or a times sign and in either order.
SEED_24_QUOTE = re.compile(
    r"\b576\b|72\s*/\s*24|\bb_?3\s*=\s*24\b|24\^2|\(2\s*\*\s*b3\)"
    r"|\b24\s*[*xX×]\s*12\b|\b12\s*[*xX×]\s*24\b"
    r"|\bb_?3\s*[*xX×]\s*12\b|\b12\s*[*xX×]\s*b_?3\b|\b12\.318")
X_FORM = re.compile(
    r"\b24\s*[xX×]\s*12\b|\b12\s*[xX×]\s*24\b"
    r"|\bb_?3\s*[xX×]\s*12\b|\b12\s*[xX×]\s*b_?3\b")
LABEL = re.compile(r"seed_24|retired seed")
NOT_A_QUOTE = ("Decimal(", "No hardcoded")

#: A comment table row: ``# <lead> | <second> | <third> [| ...]``.
TABLE_ROW = re.compile(
    r"^\s*#\s*([^|#]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*(?:\|.*)?$")
IDENT = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
#: A value cell: digits, arithmetic and the four names below, nothing else.
VALUE_CELL = re.compile(r"(?:b3|chi|phi|sqrt|[0-9.+\-*/() ])+")
TOLERANCE = 1e-9


def _unlabelled(pattern):
    return [(n, line.strip()) for n, line in enumerate(SOURCE, 1)
            if pattern.search(line)
            and not LABEL.search(line)
            and not any(tag in line for tag in NOT_A_QUOTE)]


def _evaluate(cell, reg):
    """The number a value cell states, or None when the cell is prose."""
    cell = str(cell).strip()
    if not VALUE_CELL.fullmatch(cell) or not re.search(r"\d|b3|chi|phi", cell):
        return None
    names = {"b3": reg.b3, "chi": reg.chi_eff_total,
             "phi": (1 + math.sqrt(5)) / 2, "sqrt": math.sqrt}
    return float(eval(cell, {"__builtins__": {}}, names))


def _row_key(reg, second, third):
    """The registry key a row names: its second cell, else the first word of the third."""
    head = IDENT.match(third)
    for candidate in (second, head.group(0) if head else ""):
        if IDENT.fullmatch(candidate) and isinstance(
                getattr(reg, candidate, None), (int, float)):
            return candidate
    return None


def _value_rows():
    """(line, key, stated value, served value) for every table row with a value cell."""
    reg = fr.FormulasRegistry()
    rows = []
    for n, line in enumerate(SOURCE, 1):
        m = TABLE_ROW.match(line)
        if not m:
            continue
        stated = _evaluate(m.group(1), reg)
        if stated is None:
            continue
        key = _row_key(reg, m.group(2), m.group(3))
        rows.append((n, key, stated, getattr(reg, key) if key else None))
    return rows


def _differs(stated, served):
    return abs(served - stated) > TOLERANCE * max(1.0, abs(stated))


# ------------------------------------------------------------ R2-21: x forms

def test_every_seed_24_quote_is_labelled_x_forms_included():
    for text in ("288 = 12 x b3", "(12 × b3)", "b3 x 12", "b_3 X 12",
                 "24 x 12", "12 × 24", "12 * b3"):
        assert SEED_24_QUOTE.search(text), text
    for text in ("G12 × b3", "b3 x 120", "x12", "b3 times spinor rank 12"):
        assert not SEED_24_QUOTE.search(text), text
    assert _unlabelled(SEED_24_QUOTE) == []


def test_the_labelled_x_quotes_are_read_and_say_what_the_registry_computes():
    labelled = [line for line in SOURCE
                if X_FORM.search(line) and LABEL.search(line)]
    assert any("LOGIC_CLOSURE = 288" in line for line in labelled)
    assert any("nitzotzin_roots" in line and line.lstrip().startswith("#")
               for line in labelled)
    # What the seed_24 label on those lines states, computed on both paths.
    with selection.forced({"b3_seed": "seed_24"}):
        retired = fr.FormulasRegistry()
        assert retired.nitzotzin_roots == 12 * retired.b3
    live = fr.FormulasRegistry()
    assert live.nitzotzin_roots == live.shadow_sector + live.christ_constant
    assert live.nitzotzin_roots != 12 * live.b3


# --------------------------------------------------------- R2-21: table rows

def test_table_rows_state_the_value_the_registry_serves():
    wrong = [(n, key, stated, served) for n, key, stated, served in _value_rows()
             if key and _differs(stated, served)]
    assert wrong == []


def test_every_value_row_names_a_registry_key():
    unresolved = [(n, SOURCE[n - 1].strip()) for n, key, _, _ in _value_rows()
                  if key is None]
    assert unresolved == []


def test_the_table_scan_reads_the_rows_of_all_three_tables():
    reg = fr.FormulasRegistry()
    assert _evaluate("1/144", reg) == 1 / 144
    assert _evaluate("b3", reg) == reg.b3
    assert _evaluate("chi/2", reg) == reg.chi_eff_total / 2
    assert _evaluate("phi/12", reg) != _evaluate("phi/sqrt(12)", reg)
    for prose in ("Value", "------", "P_O", "- n_gen =", ""):
        assert _evaluate(prose, reg) is None, prose
    keys = {key for _, key, _, _ in _value_rows()}
    assert {"watts_constant", "b3", "chi_eff_total", "chi_eff", "roots_total",
            "syzygy_gap", "horos_limit", "elder_kads", "mephorash_chi",
            "nitzotzin_roots", "nitsot_par", "watts_echud"} <= keys


def test_no_table_row_puts_the_retired_seed_in_the_value_column():
    """b3 rows read ``b3``: a typed 24 is right on no path but the retired one."""
    reg = fr.FormulasRegistry()
    b3_keys = {"b3", "elder_kads"}
    typed = [n for n, key, _, _ in _value_rows() if key in b3_keys
             and TABLE_ROW.match(SOURCE[n - 1]).group(1).strip() != "b3"]
    assert typed == []
    assert reg.elder_kads == reg.b3


# ------------------------------------------- R2-21: the typed symbol values

def test_typed_symbol_values_equal_the_registry():
    reg = fr.FormulasRegistry()
    wrong = []
    for key, entry in fr.FormulasRegistry.HEBREW_SYMBOL_REGISTRY.items():
        if entry["value"] is None:
            assert key in fr._PATH_VALUED_SYMBOLS, key
            continue
        stated = _evaluate(entry["value"], reg)
        assert stated is not None, (key, entry["value"])
        if _differs(stated, getattr(reg, key)):
            wrong.append((key, entry["value"], getattr(reg, key)))
    assert wrong == []


def test_get_latex_term_serves_the_boundary_the_registry_serves():
    reg = fr.FormulasRegistry()
    term = fr.FormulasRegistry.get_latex_term("horos_limit")
    assert term["value"] == reg.horos_limit == reg.horos


def test_the_unread_horos_literal_is_labelled_or_agrees():
    reg = fr.FormulasRegistry()
    lines = [line for line in SOURCE if re.match(r"\s*HOROS\s*=", line)]
    assert len(lines) == 1
    assert fr.FormulasRegistry.HOROS == reg.horos_limit or LABEL.search(lines[0])


# -------------------------------------------------------------------- R2-22

def test_the_equality_claim_is_labelled_seed_24_and_holds_only_there():
    with selection.forced({"b3_seed": "seed_24"}):
        retired = fr.FormulasRegistry()
        assert retired.pressure_divisor == retired.chi_eff_total
    live = fr.FormulasRegistry()
    assert live.pressure_divisor == live.b3 ** 2 / 4
    assert live.pressure_divisor != live.chi_eff_total
    block = [n for n, line in enumerate(SOURCE, 1)
             if re.match(r"\s*#\s*pressure_divisor\s*=\s*b3\^2/4", line)]
    assert len(block) == 1
    claims = [(n, line.strip()) for n, line in enumerate(SOURCE, 1)
              if re.search(r"equals\s+chi_eff_total", line, re.I)]
    assert [c for c in claims if not LABEL.search(c[1])] == []
