"""electroweak_mixing's v = 246.37 GeV is the retired-seed k_gimel*(b3-4) at
b3 = 24; it may not be called a geometric prediction (live seed gives 850.9)."""
from pathlib import Path

SRC = (Path(__file__).resolve().parents[1] / "src" / "metaphysica" / "simulations" / "PM"
       / "gauge" / "electroweak_mixing.py").read_text(encoding="utf-8")


def test_vev_literal_labelled_calibrated():
    assert "geometric VEV prediction" not in SRC
    assert "geometric prediction from k_gimel" not in SRC
    assert "retired-seed calibration" in SRC
