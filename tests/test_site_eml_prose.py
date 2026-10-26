"""The site claimed EML agreement unconditionally: on every certificate
gate, and on every formula with no EML variant at all. 101 of 116 run_eml
methods only return run(), so no such blanket claim holds."""
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "src" / "metaphysica" / "website" / "Pages"


def test_no_unconditional_eml_agreement_claim():
    for name in ("certificates.html", "formulas.html"):
        text = (PAGES / name).read_text(encoding="utf-8")
        for phrase in ("AGREE in cross-check", "all EML cross-checks pass",
                       "produces same result as Wolfram",
                       "eml_verify(", "agrees with Normal Math", "same result via"):
            assert phrase not in text, (name, phrase)
