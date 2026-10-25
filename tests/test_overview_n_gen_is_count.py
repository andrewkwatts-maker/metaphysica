"""The overview may call n_gen = 3 a count, not a mechanism: Y7 has no chiral
matter, so 'three generations' is OPEN (D-011, C4 audit)."""
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "src" / "metaphysica" / "simulations" / "PM"
       / "geometry" / "closed_geometry" / "overview.py").read_text(encoding="utf-8")


def test_n_gen_line_marks_chirality_open():
    assert "not a fitted number" not in SRC
    assert "chiral generations is open" in SRC
