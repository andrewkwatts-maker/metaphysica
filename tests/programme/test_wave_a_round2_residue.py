"""Wave A round 2, complete_residue_registry: R2-17 (the k_gimel paragraph of section 2.3.3
says what the code does: k_gimel and the row multipliers are typed inputs)."""
import ast
import inspect
import math

from metaphysica.simulations.PM.support import complete_residue_registry as crr


def _k_gimel_paragraph() -> str:
    blocks = crr.CompleteResidueRegistryV18().get_section_content().content_blocks
    found = [b.content for b in blocks
             if b.type == "paragraph" and isinstance(b.content, str) and "12 + 1/π" in b.content]
    assert len(found) == 1, f"expected one k_gimel paragraph, found {len(found)}"
    return found[0]


def _typed_row_multipliers(tree: ast.Module) -> list:
    """Numeric literals that multiply k_gimel inside _make_registry."""
    func = next(n for n in tree.body
                if isinstance(n, ast.FunctionDef) and n.name == "_make_registry")
    return [n.right.value for n in ast.walk(func)
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult)
            and isinstance(n.left, ast.Name) and n.left.id == "k_gimel"
            and isinstance(n.right, ast.Constant) and isinstance(n.right.value, (int, float))]


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
    assert crr.k_gimel == 12 + 1 / math.pi
    assert _typed_row_multipliers(tree)
    # The text says so, and quotes the value of the constant.
    text = _k_gimel_paragraph()
    assert "types k_ℷ in as an input" in text
    assert "types a multiplier into individual rows" in text
    assert f"≈ {crr.k_gimel:.3f}" in text
    assert "is reproduced by construction" in text and "not predicted" in text
