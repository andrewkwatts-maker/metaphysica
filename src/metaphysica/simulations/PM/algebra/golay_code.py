"""Extended binary Golay code C24 (split out of leech_lattice.py).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

import numpy as np


class GolayCode:
    """Extended binary Golay code C₂₄.

    The [24, 12, 8] binary code with 4096 codewords, minimum
    Hamming distance 8. Constructed via the Miracle Octad Generator (MOG).
    """

    # Generator matrix for the extended [24,12,8] Golay code
    # Left half is I₁₂, right half is the parity check matrix B
    # B is derived from the quadratic residue construction mod 11
    _B = np.array([
        [1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1],
        [0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1],
        [1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1],
        [0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1],
        [0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
        [0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1],
        [0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    ], dtype=np.uint8)

    def __init__(self):
        self._generator = np.hstack([np.eye(12, dtype=np.uint8), self._B])
        self._codewords = None

    @property
    def generator_matrix(self) -> np.ndarray:
        """12×24 generator matrix [I₁₂ | B]."""
        return self._generator

    def enumerate_codewords(self) -> np.ndarray:
        """Enumerate all 2¹² = 4096 codewords of C₂₄.

        Returns (4096, 24) array of binary vectors.
        """
        if self._codewords is not None:
            return self._codewords

        codewords = np.zeros((4096, 24), dtype=np.uint8)
        for i in range(4096):
            # Convert integer to binary vector of length 12
            msg = np.array([(i >> k) & 1 for k in range(12)], dtype=np.uint8)
            codewords[i] = msg @ self._generator % 2

        self._codewords = codewords
        return self._codewords

    def min_distance(self) -> int:
        """Compute the minimum Hamming distance of the code."""
        cw = self.enumerate_codewords()
        min_weight = 24  # upper bound
        for i in range(1, len(cw)):  # skip zero codeword
            w = np.sum(cw[i])
            if 0 < w < min_weight:
                min_weight = int(w)
        return min_weight

    def weight_distribution(self) -> dict:
        """Compute the weight distribution {weight: count}."""
        cw = self.enumerate_codewords()
        weights = np.sum(cw, axis=1)
        dist = {}
        for w in weights:
            w = int(w)
            dist[w] = dist.get(w, 0) + 1
        return dist

    def verify(self) -> dict:
        """Verify Golay code properties."""
        cw = self.enumerate_codewords()
        wd = self.weight_distribution()
        return {
            'num_codewords': len(cw) == 4096,
            'min_distance_8': self.min_distance() == 8,
            'weight_0_count': wd.get(0, 0) == 1,
            'weight_24_count': wd.get(24, 0) == 1,
            'weight_8_count': wd.get(8, 0) == 759,
            'weight_12_count': wd.get(12, 0) == 2576,
            'weight_16_count': wd.get(16, 0) == 759,
        }
