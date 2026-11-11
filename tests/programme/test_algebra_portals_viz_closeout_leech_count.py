"""L6 close-out XA-14: the Leech lattice minimal-vector count, 196,560, from the three
shapes counted on the Golay code object (a verification test, like misc-45's 4096)."""
from math import comb

from metaphysica.simulations.PM.algebra.leech_lattice import LeechLattice


def test_leech_minimal_vector_count_is_196560():
    lattice = LeechLattice()
    weights = lattice.golay.weight_distribution()
    n_octads, n_words = int(weights[8]), int(sum(weights.values()))
    assert (n_octads, n_words) == (759, 4096)
    shapes = 4 * comb(24, 2) + n_octads * 2 ** 7 + 24 * n_words
    assert shapes == 1104 + 97152 + 98304 == 196560
    assert lattice.kissing_number == shapes
