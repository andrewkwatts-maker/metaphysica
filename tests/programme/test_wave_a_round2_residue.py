"""Wave A round 2, complete_residue_registry: R2-17 (the k_gimel paragraph of section 2.3.3
says what the code does: k_gimel and the row multipliers are typed inputs) and its review
round (the retired-reading label, the rule per block of rows, the electron mass read from the
loader, the 'sterile' sentence stated as a proposal)."""
import ast
import inspect
import math
import re

from metaphysica.generators import superseded_scan as scan
from metaphysica.simulations.core.FormulasRegistry import get_registry
from metaphysica.simulations.PM.algebra._active_b3 import active_b3
from metaphysica.simulations.PM.geometry.b3_path import seed_values
from metaphysica.simulations.PM.support import complete_residue_registry as crr


def _paragraph(marker: str) -> str:
    blocks = crr.CompleteResidueRegistryV18().get_section_content().content_blocks
    found = [b.content for b in blocks
             if b.type == "paragraph" and isinstance(b.content, str) and marker in b.content]
    assert len(found) == 1, f"expected one paragraph with {marker!r}, found {len(found)}"
    return found[0]


def _k_gimel_paragraph() -> str:
    return _paragraph("12 + 1/π")


def _make_registry_node(tree: ast.Module) -> ast.FunctionDef:
    return next(n for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name == "_make_registry")


def _typed_row_multipliers(tree: ast.Module) -> list:
    """Numeric literals that multiply k_gimel inside _make_registry."""
    return [n.right.value for n in ast.walk(_make_registry_node(tree))
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult)
            and isinstance(n.left, ast.Name) and n.left.id == "k_gimel"
            and isinstance(n.right, ast.Constant) and isinstance(n.right.value, (int, float))]


def _rule_shapes_by_category(tree: ast.Module) -> dict:
    """Per category, the lambda_n expressions of _make_registry with their numbers blanked."""
    shapes: dict = {}
    for call in ast.walk(_make_registry_node(tree)):
        if isinstance(call, ast.Call) and getattr(call.func, "id", "") == "SpectralResidue":
            kw = {k.arg: k.value for k in call.keywords}
            shape = re.sub(r"Constant\(value=[^)]*\)", "N", ast.dump(kw["lambda_n"]))
            shapes.setdefault(ast.unparse(kw["category"]), set()).add(shape)
    return shapes


def test_k_gimel_paragraph_makes_no_derivation_claim():
    text = _k_gimel_paragraph()
    assert "derived" not in text
    assert "single geometric input" not in text
    assert "reproduced from" not in text


def test_k_gimel_paragraph_says_what_the_code_types():
    tree = ast.parse(inspect.getsource(crr))
    assign = next(n for n in tree.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "k_gimel" for t in n.targets))
    # The code: k_gimel is a typed expression (no call, no reader), and rows carry typed multipliers.
    assert not any(isinstance(n, ast.Call) for n in ast.walk(assign.value))
    # 2026-11-11: the typed 12 is b3/2 at the retired seed_24 reading (b3 read from b3_path.PATHS,
    # not typed here). When k_gimel is read from the path this line and the line above fail and
    # the paragraph must be rewritten.
    assert crr.k_gimel == seed_values("seed_24")[0] / 2 + 1 / math.pi
    assert _typed_row_multipliers(tree)
    # The text says so, and quotes the value of the constant.
    text = _k_gimel_paragraph()
    assert "types k_ℷ in as an input" in text
    assert "types a multiplier into individual rows" in text
    assert f"≈ {crr.k_gimel:.3f}" in text
    assert "is reproduced by construction" in text and "not predicted" in text


def test_k_gimel_paragraph_labels_the_typed_value_as_the_retired_reading():
    """Rule 6: 12 + 1/π is off-path; the text says so and gives the engine value in force."""
    text = _k_gimel_paragraph()
    retired_b3 = seed_values("seed_24")[0]
    assert ("12 + 1/π is the value b₃/2 + 1/π takes at the retired seed_24 reading "
            f"(b₃ = {retired_b3})") in text
    engine = get_registry().demiurgic_coupling  # the engine's k_gimel, b3/2 + 1/pi on the path
    assert engine == active_b3() / 2 + 1 / math.pi
    assert f"on the path in force (b₃ = {active_b3()}) the engine's k_ℷ is {engine:.3f}" in text
    # The cited retired b3 is labelled as retired, so the superseded-prose scan has no active hit.
    hits = scan.scan_sections({"x": {"contentBlocks": [{"content": text}]}})
    assert scan.active_hits(hits) == []


def test_rule_is_typed_per_block_of_rows_not_per_category():
    """Rule 4: one category carries several lambda_n rules in _make_registry; the text says so."""
    shapes = _rule_shapes_by_category(ast.parse(inspect.getsource(crr)))
    several = sorted(c for c, rules in shapes.items() if len(rules) > 1)
    assert "ResidueCategory.MASS_SCALE" in several, shapes.keys()
    text = _k_gimel_paragraph()
    assert "for the row's category" not in text
    assert ("Each eigenvalue is set by a rule typed for its block of rows "
            "(one category can carry several rules)") in text


def test_electron_mass_in_the_paragraph_is_read_from_the_loader(monkeypatch):
    """Rule 6: the quoted electron mass follows the loader value, it is not typed."""
    real = crr._pdg_v
    assert f"(~{real('leptons', 'm_electron') * 1e3:.3f} MeV)" in _k_gimel_paragraph()

    def moved(category: str, name: str) -> float:
        return 0.002 if (category, name) == ("leptons", "m_electron") else real(category, name)

    monkeypatch.setattr(crr, "_pdg_v", moved)
    assert "the electron mass (~2.000 MeV)" in _k_gimel_paragraph()


def test_sterile_sentence_is_a_proposal_and_does_not_contradict_the_typed_rules(monkeypatch):
    """Rule 6: section 2.3.3 no longer states as fact that topology fixes the residues."""
    text = _paragraph("<em>sterile</em>")
    assert "they are determined by the manifold's topology" not in text
    assert "This topological encoding is what makes" not in text
    assert "The proposal is that this topological encoding makes the residues" in text
    assert "This module does not compute them from the topology" in text
    assert "typed rules with typed inputs (next paragraph)" in text
    # chi in that paragraph is the value proton_decay_text() reads, not a typed 144.
    moved = dict(crr.proton_decay_text(), chi="CHI")
    monkeypatch.setattr(crr, "proton_decay_text", lambda: moved)
    assert "χ(V₇) = CHI at s = 3/2" in _paragraph("<em>sterile</em>")
