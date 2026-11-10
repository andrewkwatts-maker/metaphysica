"""CERTIFICATES.py is split into gate-group mixins; every gate stays on the validator."""
from pathlib import Path

from metaphysica.simulations.PM.validation import CERTIFICATES
from metaphysica.simulations.PM.validation.CERTIFICATES import PrincipiaValidator

VAL = Path(CERTIFICATES.__file__).parent
GATES = sorted((VAL / "certificate_gates").glob("*.py"))


def test_all_gates_present():
    names = {n for n in dir(PrincipiaValidator) if n.startswith("cert_")}
    assert len(names) == 27
    assert {"cert_c003_chi_effective", "cert_g81_asymptotic_safety_fixed_point",
            "cert_pairs_bridge", "cert_hyst_044"} <= names


def test_files_are_small():
    for p in [VAL / "CERTIFICATES.py", *GATES]:
        assert len(p.read_text(encoding="utf-8").splitlines()) <= 500, p.name


def test_each_gate_lives_in_one_group_file_not_the_validator():
    assert "def cert_" not in (VAL / "CERTIFICATES.py").read_text(encoding="utf-8")
    assert len([p for p in GATES if p.name != "__init__.py"]) == 7
