"""Round 5: leech_lattice.py split so no file passes the 500-line limit (sim-algebra-misc-37)."""
from pathlib import Path

from metaphysica.simulations.PM.algebra import golay_code, leech_decomposition, leech_lattice

LIMIT = 500


def test_leech_modules_within_line_limit():
    for mod in (golay_code, leech_decomposition, leech_lattice):
        n = len(Path(mod.__file__).read_text(encoding="utf-8").splitlines())
        assert n <= LIMIT, (mod.__name__, n)


def test_leech_lattice_keeps_public_api():
    lat = leech_lattice.LeechLattice()
    assert leech_lattice.GolayCode is golay_code.GolayCode
    assert isinstance(lat, leech_decomposition.LeechDecompositionMixin)
    assert lat.dimension == 24
    assert lat.decompose_e8_triple()["orthogonal"] is True
    assert golay_code.GolayCode().min_distance() == 8
