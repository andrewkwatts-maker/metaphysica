"""XP-05: FormulasRegistry comments that quote seed-24 arithmetic are labelled.

576 = 24^2, 72/24 = 3, b3 = 24, 2*b3 = 48, 288 = b3 * 12 = 24 * 12 and
kappa_Delta = b3/2 + 1/pi = 12.318 hold only at the retired seed b3 = 24. Each
such quote is either path-generic (no number) or carries a seed_24 label on its
own line. The close-out review widened the pattern to the 24 * 12, b3 * 12 and
12.318 quotes and added the symbol-map check: a LATEX_REGISTRY comment that
leads with a number must equal the registry value on the path in force.
"""
import importlib
import re
from pathlib import Path

fr = importlib.import_module("metaphysica.simulations.core.FormulasRegistry")

SOURCE = Path(fr.__file__).read_text(encoding="utf-8").splitlines()

SEED_24_QUOTE = re.compile(
    r"\b576\b|72\s*/\s*24|\bb_?3\s*=\s*24\b|24\^2|\(2\s*\*\s*b3\)"
    r"|\b24\s*\*\s*12\b|\bb3\s*\*\s*12\b|\b12\.318")
LABEL = re.compile(r"seed_24|retired seed")
NOT_A_QUOTE = ("Decimal(", "No hardcoded")


def _unlabelled():
    return [(n, line.strip()) for n, line in enumerate(SOURCE, 1)
            if SEED_24_QUOTE.search(line)
            and not LABEL.search(line)
            and not any(tag in line for tag in NOT_A_QUOTE)]


def test_every_seed_24_quote_is_labelled():
    assert _unlabelled() == []


def test_the_scan_sees_the_labelled_quotes():
    labelled = [line for line in SOURCE
                if SEED_24_QUOTE.search(line) and LABEL.search(line)]
    assert len(labelled) >= 10


def test_module_docstring_reads_n_gen_from_the_path():
    doc = fr.FormulasRegistry.__doc__
    assert "72/24" not in doc
    assert "chi_eff_route" in doc


def test_chi_eff_docstring_is_path_generic():
    doc = fr.FormulasRegistry.chi_eff.__doc__
    assert "72" not in doc
    assert "chi_eff_route" in doc


def test_pressure_divisor_docstring_does_not_type_576():
    doc = fr.FormulasRegistry.pressure_divisor.__doc__
    assert "seed_24" in doc
    assert "= 144" not in doc


#: A symbol-map entry whose comment leads with a number (or a fraction).
SYMBOL_MAP_LINE = re.compile(
    r'^\s*"(\w+)":\s*r?"[^"]*",\s*#\s*([0-9.]+)(?:\s*/\s*([0-9.]+))?\s+-\s')


def _symbol_map_mismatches():
    reg = fr.FormulasRegistry()
    out = []
    for n, line in enumerate(SOURCE, 1):
        m = SYMBOL_MAP_LINE.match(line)
        if not m or LABEL.search(line):
            continue
        quoted = float(m.group(2)) / (float(m.group(3)) if m.group(3) else 1.0)
        value = getattr(reg, m.group(1), None)
        if not isinstance(value, (int, float)):
            continue
        if abs(value - quoted) > 1e-3 * max(1.0, abs(quoted)):
            out.append((n, m.group(1), quoted, value))
    return out


def test_symbol_map_comments_quote_the_path_value():
    assert _symbol_map_mismatches() == []


def test_symbol_map_scan_reads_the_numbered_comments():
    numbered = [line for line in SOURCE if SYMBOL_MAP_LINE.match(line)]
    assert len(numbered) >= 15


def test_roots_total_docstring_is_path_generic():
    doc = fr.FormulasRegistry.roots_total.__doc__
    assert "288 = b3" not in doc and "D_space_12" not in doc
    assert "shadow_sector + christ_constant" in doc
    assert "seed_24" in doc
