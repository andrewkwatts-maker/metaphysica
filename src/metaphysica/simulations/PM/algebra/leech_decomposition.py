"""Sublattice decompositions of the Leech ambient space (mixin for LeechLattice).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

import numpy as np


class LeechDecompositionMixin:
    """E8 triple, bridge pairs, four-face grouping and axion alignment."""

    def decompose_e8_triple(self) -> dict:
        """Decompose the 24D ambient space into three E8-structured 8D blocks.

        The decomposition R²⁴ = R⁸ ⊕ R⁸ ⊕ R⁸ assigns coordinates
        [0:8], [8:16], [16:24] to three blocks. Each block carries
        the geometry of an E8 lattice (same inner product structure,
        same root system symmetries).

        Important: The Leech lattice itself has NO norm-2 vectors,
        so the sublattice of Leech restricted to any 8D block is NOT E8.
        Rather, we decompose the *ambient space* — the E8 structure
        describes the geometry of each block, and Leech vectors
        project onto these blocks compatibly.

        Returns:
            Dict with sublattice data and verification results
        """
        from metaphysica.simulations.PM.algebra.e8_root_system import E8RootSystem

        e8 = E8RootSystem()

        # Three 8D blocks
        blocks = []
        for idx in range(3):
            basis = e8.e8_sublattice_basis(idx)  # (8, 24)
            blocks.append(basis)

        # Verify orthogonality: blocks are in disjoint coordinate ranges
        orthogonal = True
        for i in range(3):
            for j in range(i + 1, 3):
                overlap = np.sum(blocks[i] * blocks[j])
                if abs(overlap) > 1e-10:
                    orthogonal = False

        # Verify each block recovers E8 Cartan matrix
        e8_cartan = e8.cartan_matrix
        cartan_match = True
        for idx in range(3):
            simple = blocks[idx]  # (8, 24)
            # Compute Cartan matrix from embedded simple roots
            gram = simple @ simple.T  # (8, 8) = inner products
            local_cartan = np.zeros((8, 8), dtype=np.int64)
            for i in range(8):
                for j in range(8):
                    local_cartan[i, j] = round(2 * gram[i, j] / gram[j, j])
            if not np.array_equal(local_cartan, e8_cartan):
                cartan_match = False

        # Verify spans R24
        all_basis = np.vstack(blocks)  # (24, 24)
        rank = np.linalg.matrix_rank(all_basis)

        return {
            'sublattices': blocks,
            'dimensions': [8, 8, 8],
            'total_dim': 24,
            'orthogonal': orthogonal,
            'each_is_e8': cartan_match,
            'spans_R24': rank == 24,
            'e8_cartan': e8_cartan,
        }

    def extract_e8_pair(self) -> dict:
        """Extract E8×E8 (16D) plus remaining 8D.

        The first two E8 copies (coordinates [0:16]) form E8×E8,
        the heterotic string gauge group. The remaining 8D
        (coordinates [16:24]) corresponds to spacetime dimensions.

        Cross-references E8RootSystem.e8_cross_e8_roots() for the
        480-root system in R¹⁶.

        Returns:
            Dict with E8×E8 data and remaining basis
        """
        from metaphysica.simulations.PM.algebra.e8_root_system import E8RootSystem

        e8 = E8RootSystem()

        # E8×E8: 480 roots in R16, embedded in first 16 coords of R24
        e8xe8_r16 = e8.e8_cross_e8_roots()  # (480, 16)
        e8xe8_r24 = np.zeros((480, 24), dtype=np.float64)
        e8xe8_r24[:, :16] = e8xe8_r16

        # Remaining 8D basis
        remaining_basis = np.zeros((8, 24), dtype=np.float64)
        for i in range(8):
            remaining_basis[i, 16 + i] = 1.0

        # Verification
        all_norms = np.sum(e8xe8_r16 ** 2, axis=1)

        return {
            'e8_pair_roots': e8xe8_r24,
            'e8_pair_roots_r16': e8xe8_r16,
            'num_roots': 480,
            'remaining_basis': remaining_basis,
            'remaining_dim': 8,
            'all_norm2': bool(np.allclose(all_norms, 2.0)),
            'heterotic_compatible': True,
        }

    def decompose_bridge_pairs(self) -> dict:
        """Decompose 24D into 12 two-dimensional sublattices (bridge pairs).

        Each bridge B_i corresponds to a 2D coordinate plane in R²⁴:
          B₀ = span(e₀, e₁), B₁ = span(e₂, e₃), ..., B₁₁ = span(e₂₂, e₂₃)

        The bridge moduli (L1, L2, θ) are extracted from the Leech
        generator matrix restricted to each 2D block.

        Returns:
            Dict with 12 bridge pair data including moduli
        """
        gen = self._generator_matrix()  # (24, 24)

        pairs = []
        sublattice_bases = []
        moduli = np.zeros((12, 3), dtype=np.float64)

        for b in range(12):
            c0 = 2 * b
            c1 = 2 * b + 1
            pairs.append((c0, c1))

            # Extract the 2D sublattice basis from generator matrix
            # Use the two generator rows that have primary support in this pair
            v1 = gen[c0]  # Full 24D vector
            v2 = gen[c1]  # Full 24D vector

            # Project to the 2D subspace
            v1_2d = np.array([v1[c0], v1[c1]])
            v2_2d = np.array([v2[c0], v2[c1]])

            sublattice_bases.append(np.array([v1_2d, v2_2d]))

            # Compute bridge moduli from the 2D basis vectors
            L1 = np.linalg.norm(v1_2d)
            L2 = np.linalg.norm(v2_2d)

            if L1 > 1e-10 and L2 > 1e-10:
                cos_theta = np.dot(v1_2d, v2_2d) / (L1 * L2)
                cos_theta = np.clip(cos_theta, -1.0, 1.0)
                theta = np.arccos(cos_theta)
            else:
                # Fallback for degenerate basis
                L1 = max(L1, 1.0)
                L2 = max(L2, 1.0)
                theta = np.pi / 2

            moduli[b] = [L1, L2, theta]

        # Verify: bridge pairs partition all 24 coordinates exactly
        all_coords = set()
        for c0, c1 in pairs:
            all_coords.add(c0)
            all_coords.add(c1)
        covers_all_24 = (all_coords == set(range(24)))

        num_bridges = len(pairs)
        total_dim = num_bridges * 2

        # Check within each E8 triple block:
        # Bridge b spans coords (2b, 2b+1), so it lives in E8 block floor(2b/8) = floor(b/4)
        e8_grouping = {
            0: list(range(0, 4)),    # bridges 0-3 in E8 copy 0
            1: list(range(4, 8)),    # bridges 4-7 in E8 copy 1
            2: list(range(8, 12)),   # bridges 8-11 in E8 copy 2
        }

        # Verify E8 triple consistency: each bridge's coords must lie
        # entirely within one 8D E8 block ([0:8], [8:16], [16:24])
        e8_consistent = True
        for b_idx, (c0, c1) in enumerate(pairs):
            block_c0 = c0 // 8
            block_c1 = c1 // 8
            expected_block = b_idx // 4
            if block_c0 != block_c1 or block_c0 != expected_block:
                e8_consistent = False

        return {
            'pairs': pairs,
            'sublattice_bases': sublattice_bases,
            'moduli': moduli,
            'total_dim': total_dim,
            'num_bridges': num_bridges,
            'covers_all_24': covers_all_24,
            'e8_grouping': e8_grouping,
            'consistent_with_e8_triple': e8_consistent,
        }

    def four_face_grouping(self) -> dict:
        """Group 12 bridge pairs into 4 faces of 3 bridges each.

        Face i contains bridges {i, i+4, i+8} — one bridge from
        each E8 copy. This gives:
          - 4 faces = h^{1,1} (Kähler moduli)
          - 3 bridges per face = n_gen (fermion generations)

        The grouping is:
          Face 0: bridges {0, 4, 8}   (one from each E8)
          Face 1: bridges {1, 5, 9}
          Face 2: bridges {2, 6, 10}
          Face 3: bridges {3, 7, 11}

        Returns:
            Dict with face assignments and consistency checks
        """
        faces = {}
        for face_idx in range(4):
            face_bridges = [face_idx + 4 * e8_copy for e8_copy in range(3)]
            faces[face_idx] = face_bridges

        # Verify every bridge appears exactly once
        all_bridges = []
        for bridges in faces.values():
            all_bridges.extend(bridges)
        all_bridges_set = set(all_bridges)

        # Verify each face has one bridge from each E8 copy
        cross_e8 = True
        for face_idx, bridges in faces.items():
            e8_copies = [b // 4 for b in bridges]
            if set(e8_copies) != {0, 1, 2}:
                cross_e8 = False

        return {
            'faces': faces,
            'num_faces': 4,
            'bridges_per_face': 3,
            'total_bridges': len(all_bridges),
            'all_bridges_covered': all_bridges_set == set(range(12)),
            'no_duplicates': len(all_bridges) == len(all_bridges_set),
            'cross_e8': cross_e8,
            'n_gen_consistent': 3 == self.dimension // 8,
            'h11_consistent': 4 == len(faces),
        }

    def compute_axion_alignment_matrix(self) -> dict:
        """Compute the KNP alignment matrix Q_{ij} from Leech lattice structure.

        In KNP (Kim-Nilles-Peloso) alignment, N axions with individual
        decay constants f_i produce an effective decay constant:
            f_eff^2 = sum_{ij} Q_{ij} f_i f_j

        For identical f_i = f_sub:
            f_eff = f_sub * sqrt(sum_{ij} Q_{ij})

        The alignment matrix Q comes from the inner product structure
        of the Leech lattice generator matrix when decomposed into
        12 bridge pairs. Specifically:

            Q_{ij} = sum_k  <gen_k|_pair_i , gen_k|_pair_j>

        where gen_k is the k-th generator row and |_pair_i denotes
        projection onto the 2D coordinate plane of bridge pair i.

        Result:
            sum Q_{ij} = 242 (not 288 = 12 * 24)
            f_eff_factor = sqrt(242) ≈ 15.56
            Ratio to sqrt(N_ax * b3) = sqrt(242/288) = 11/12 ≈ 0.917

        The factor 11/12 arises because the Golay-based generator matrix
        has off-diagonal couplings between bridge pairs (via the parity
        check matrix B), and these couplings redistribute the total norm
        relative to the naive product N_ax * b3 = 12 * 24.

        Honesty assessment: The alignment matrix is CONSTRUCTED, not
        DERIVED in a physics sense. The decomposition of R^24 into
        12 coordinate pairs is a CHOICE (see decompose_bridge_pairs
        docstring). The Q_{ij} entries depend on this choice and on
        the particular generator matrix used. A different but equally
        valid Leech generator would give a different Q. The sqrt(N*b3)
        factor in the KNP formula is dimensional analysis (counting
        degrees of freedom), and the Leech lattice provides a specific
        geometric realization that modifies this by the factor 11/12.

        Gemini debate summary (WP 2.3, 2026-03-16):
        - Round 1: Gemini argued 11/12 is "not an artifact of basis choice
          but a direct consequence of the specific algebraic and geometric
          properties of the Leech lattice as defined by Construction A and
          the Golay code." Claims it reflects inherent correlations when
          projected onto coordinate pairs.
        - Round 2: When challenged on basis dependence, Gemini pivoted to
          spherical design properties: the norm-4 shell of the Leech lattice
          forms a spherical 11-design, making certain averages over all
          196,560 minimal vectors basis-independent. However, this is a
          different (and more canonical) computation than our generator-
          based Q_{ij}. A basis-independent alignment would use the full
          minimal vector set, not the generator matrix.
        - Round 3: Classification: CONSTRUCTED. "The specific Construction A
          generator and the way pairs are defined and projected introduce
          non-canonical choices. The resulting numerical values are derived
          from this specific construction, rather than being inherent,
          axiomatically necessary properties of the Leech lattice."

        Returns:
            dict with:
            - Q: (12,12) alignment matrix
            - f_eff_factor: sqrt(sum Q_{ij}) = effective enhancement
            - sqrt_N_b3: sqrt(12*24) for comparison
            - comparison_ratio: f_eff_factor / sqrt(N*b3)
            - ratio_exact: '11/12' if ratio matches
            - trace: trace of Q
            - diagonal: diagonal entries of Q
            - derivation_honest: False — depends on generator choice
        """
        gen = self._generator_matrix()  # (24, 24) scaled generator

        # Compute alignment matrix Q_{ij}
        # Q_{ij} = sum over generator rows k of the dot product
        # between the 2D projections onto bridge pair i and pair j
        Q = np.zeros((12, 12), dtype=np.float64)
        for i in range(12):
            ci = slice(2 * i, 2 * i + 2)
            for j in range(12):
                cj = slice(2 * j, 2 * j + 2)
                for k in range(24):
                    Q[i, j] += np.dot(gen[k, ci], gen[k, cj])

        # Derived quantities
        q_sum = float(np.sum(Q))
        f_eff_factor = float(np.sqrt(q_sum))
        sqrt_N_b3 = float(np.sqrt(12.0 * 24.0))
        ratio = f_eff_factor / sqrt_N_b3

        # Check if ratio is exactly 11/12
        ratio_exact = None
        if abs(ratio - 11.0 / 12.0) < 1e-10:
            ratio_exact = '11/12'

        return {
            'Q': Q,
            'Q_sum': q_sum,
            'f_eff_factor': f_eff_factor,
            'sqrt_N_b3': sqrt_N_b3,
            'comparison_ratio': ratio,
            'ratio_exact': ratio_exact,
            'trace': float(np.trace(Q)),
            'diagonal': np.diag(Q).tolist(),
            'derivation_honest': False,
            'superseded_by': 'compute_axion_alignment_from_shell',
            'honesty_note': (
                'The alignment matrix Q depends on the choice of Leech '
                'generator matrix and the coordinate-pair decomposition '
                'of R^24. Different valid generators yield different Q. '
                'The 11/12 ratio is an artifact of this particular '
                'Construction A generator, not a canonical lattice invariant.'
            ),
        }

    def minimal_vectors_shell(self) -> np.ndarray:
        """Every minimal vector of the selected lattice.

        196560 of norm 4 for Leech, 720 of norm 2 for E8^3. This is the
        canonical, basis-free object: the generator matrix is one of many
        valid bases, but the shell is determined by the lattice itself.
        """
        import itertools

        if self._lattice_choice() == "niemeier_e8x3":
            E8 = self._e8_basis()
            Einv = np.linalg.inv(E8)

            def in_e8(v):
                c = v @ Einv
                return np.allclose(c, np.round(c), atol=1e-9)

            block = []
            for i, j in itertools.combinations(range(8), 2):
                for si in (1.0, -1.0):
                    for sj in (1.0, -1.0):
                        v = np.zeros(8)
                        v[i], v[j] = si, sj
                        if in_e8(v):
                            block.append(v)
            for signs in itertools.product((0.5, -0.5), repeat=8):
                v = np.array(signs)
                if abs(v @ v - 2.0) > 1e-12:
                    continue
                if sum(1 for s in signs if s < 0) % 2 != 0:
                    continue
                if in_e8(v):
                    block.append(v)
            out = []
            for k in range(3):
                for b in block:
                    v = np.zeros(24)
                    v[8 * k:8 * (k + 1)] = b
                    out.append(v)
            return np.array(out)

        words = np.asarray(self.golay.enumerate_codewords()) % 2
        octads = [w for w in words if int(w.sum()) == 8]
        out = []
        for i, j in itertools.combinations(range(24), 2):
            for si in (4, -4):
                for sj in (4, -4):
                    v = np.zeros(24)
                    v[i], v[j] = si, sj
                    out.append(v)
        for oc in octads:
            sup = np.flatnonzero(oc)
            for bits in range(1 << 8):
                s = np.array([1 if (bits >> k) & 1 == 0 else -1 for k in range(8)])
                if s.prod() != 1:
                    continue
                v = np.zeros(24)
                v[sup] = 2 * s
                out.append(v)
        for w in words:
            base = np.where(w == 1, -1.0, 1.0)
            for pos in range(24):
                v = base.copy()
                v[pos] = -3 * base[pos]
                out.append(v)
        V = np.array(out) / np.sqrt(8.0)
        return V[np.abs((V * V).sum(1) - 4.0) < 1e-9]

    def compute_axion_alignment_from_shell(self) -> dict:
        """The KNP alignment matrix computed basis-independently, and the
        result: there is no alignment.

        compute_axion_alignment_matrix sums over the 24 GENERATOR ROWS and
        flags itself `derivation_honest: False`, because a different valid
        basis for the same lattice gives a different Q. Round 2 of the debate
        recorded in that method named the fix -- average over the full minimal
        vector set instead, which is basis-free -- and it was never applied.

        Applied, it is decisive. Aut(L) acts irreducibly on the span, so
        sum_v v_a v_b over a complete shell is forced to be proportional to
        delta_ab, and Q comes out proportional to the IDENTITY:

            Leech shell (196560 vectors) : Q = 65520 * I, off-diag max 2.5e-13
            E8^3 shell  (720 vectors)    : Q =   120 * I, off-diag max 0
            (generator rows, for contrast: condition number 49827)

        The counts check independently: 196560 * 4 / 24 * 2 = 65520 and
        720 * 2 / 24 * 2 = 120.

        PHYSICS: KNP alignment is an enhancement produced by OFF-DIAGONAL
        correlations between axion directions. An isotropic Q has none, so
        the lattice contributes no alignment enhancement whatsoever. The
        structure visible in the generator-based Q is a property of the basis
        that was chosen, not of the lattice -- which is what the original
        honesty note suspected and did not compute. The finding is stronger
        than that note: not only the 11/12 ratio but the entire off-diagonal
        structure is an artifact.

        Returns a dict whose `derivation_honest` is True, because nothing here
        depends on a choice: the shell is canonical and the isotropy is forced.
        """
        V = self.minimal_vectors_shell()
        Q = np.zeros((12, 12), dtype=np.float64)
        for i in range(12):
            ci = slice(2 * i, 2 * i + 2)
            for j in range(12):
                cj = slice(2 * j, 2 * j + 2)
                Q[i, j] = float(np.sum(V[:, ci] * V[:, cj]))

        off = Q - np.diag(np.diag(Q))
        scale = max(1.0, float(abs(np.trace(Q))))
        is_diagonal = bool(np.abs(off).max() < 1e-6 * scale)
        eig = np.linalg.eigvalsh(Q)

        return {
            "lattice": self._lattice_choice(),
            "n_vectors": int(len(V)),
            "Q": Q,
            "Q_sum": float(Q.sum()),
            "trace": float(np.trace(Q)),
            "max_abs_offdiagonal": float(np.abs(off).max()),
            "is_diagonal": is_diagonal,
            "eigenvalues": eig.tolist(),
            "condition_number": float(eig.max() / eig.min()) if eig.min() > 0 else None,
            "alignment_enhancement": not is_diagonal,
            "derivation_honest": True,
            "note": (
                "Averaged over the complete minimal-vector shell, which is "
                "basis-free, Q is proportional to the identity. KNP alignment "
                "requires off-diagonal correlation between axion directions; "
                "an isotropic Q supplies none, so the lattice contributes no "
                "alignment enhancement. The off-diagonal structure in "
                "compute_axion_alignment_matrix comes from the choice of "
                "generator basis, not from the lattice."
            ),
        }
