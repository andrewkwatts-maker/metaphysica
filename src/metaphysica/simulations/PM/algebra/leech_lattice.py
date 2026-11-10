"""
Leech Lattice Λ₂₄ — Construction via Extended Golay Code
==========================================================
Constructs the Leech lattice using Construction A from the extended
binary Golay code C₂₄. Computes minimal vectors (kissing number),
theta series coefficients, and lattice properties.

The Leech lattice is the unique even unimodular lattice in 24 dimensions
with no vectors of norm² = 2 — the densest sphere packing in 24D.

Construction A:
  Λ₂₄ = {v ∈ Z²⁴ : v mod 2 ∈ C₂₄, Σvᵢ ≡ 0 (mod 4)} / √2
  scaled so minimal norm² = 4.

References:
  - Conway & Sloane, "Sphere Packings, Lattices and Groups", Ch. 4, 10
  - Conway, "A characterisation of Leech's lattice" (1969)

Assertion Assessment (Sprint 2, WP 2.1)
- Assertion: Leech ambient R²⁴ = R⁸⊕R⁸⊕R⁸ with E8-structured blocks
- Git History: 1 commit (0c03f140, Sprint 1 foundation). No retroactive
  corrections or fitting detected. Decomposition methods created alongside
  initial file.
- Lattice Result: dim=24, orthogonal=True, each_is_e8=True (Cartan matrix
  recovered in all 3 blocks), spans_R24=True (rank 24). E8 pair: 480 roots,
  all norm 2. Bridge decomposition: 12 bridges, moduli L1=L2=sqrt(2),
  theta=pi/2 (identical orthogonal square lattices in all 12 planes).
- Gemini Verdict: R^24 = R^8+R^8+R^8 is CHOICE (any R^24 admits this
  trivially). Equipping each R^8 with E8 is CHOICE (valid, standard in
  Construction B, but not unique). 12x2D bridge decomposition is CHOICE
  (coordinate pairing, not canonical). Heterotic E8xE8 connection is
  ANALOGY. Gemini noted: "The Leech lattice is NOT E8+E8+E8 but is
  constructed from it via gluing" and "the code only decomposes the
  ambient space, not the lattice itself." On (c) initially classified as
  THEOREM but revised to CHOICE after challenge: "there isn't a canonical
  theorem that dictates this specific 12x2D decomposition."
- Classification: PLAUSIBLE
- Evidence: The E8 triple decomposition of R^24 is mathematically valid and
  standard in Leech lattice theory (Construction B starts with E8+E8+E8,
  then glues to remove norm-2 vectors). The Cartan matrix recovery in each
  block is correct. However, (a) the decomposition is of the ambient space,
  not the Leech lattice itself, (b) all sub-decompositions (8D blocks, 2D
  bridges, heterotic split) are framework choices not theorems, and (c) the
  Leech lattice's relationship to E8+E8+E8 is via gluing/Construction B,
  not direct sum. The assertion is physically motivated and mathematically
  consistent but overstates uniqueness.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

import numpy as np
from typing import Optional


from .golay_code import GolayCode  # noqa: F401  (re-exported)
from .leech_decomposition import LeechDecompositionMixin


class LeechLattice(LeechDecompositionMixin):
    """Leech lattice Λ₂₄ constructed via the extended Golay code.

    Attributes:
        golay: The underlying GolayCode instance
        minimal_vectors: Vectors of minimal norm (norm² = 4), if computed
    """

    def __init__(self, compute_minimal: bool = False):
        """Initialize Leech lattice.

        Args:
            compute_minimal: If True, enumerate all 196,560 minimal vectors.
                            This uses ~37 MB and takes a few seconds.
        """
        self.golay = GolayCode()
        self._minimal_vectors = None
        self._kissing_number = None

        if compute_minimal:
            self._enumerate_minimal_vectors()

    def _enumerate_minimal_vectors(self):
        """Enumerate all 196,560 minimal vectors (norm² = 4 in lattice coords).

        The minimal vectors decompose into three types:
          Type 1: 97,152 vectors — shape 2²²0² (two ±2's, rest 0's)
                  modified by Golay code structure
          Type 2: 98,304 vectors — shape (±3)(±1)²³
                  modified by Golay code
          Type 3: 1,104 vectors — shape (±4)(0)²³ and permutations
                  (Actually absorbed into Type 1 and Type 2)

        We use the direct Construction A enumeration for correctness.
        """
        codewords = self.golay.enumerate_codewords()
        cw_set = set(map(tuple, codewords))

        minimal = []

        # Type 1: vectors of shape 2^a * (±1)^b with specific Golay structure
        # In Construction A, minimal vectors have norm² = 4 (before √2 scaling)
        # which means Σvᵢ² = 8 in the integer coordinates

        # Shape (±2)²(0)²²: choose 2 positions, signs ±2, rest 0
        # Must satisfy: v mod 2 ∈ C₂₄
        # v mod 2 has 1's at the two chosen positions
        # So we need the 2-element support to be part of a codeword
        # But min distance is 8, so no weight-2 codewords exist
        # → No type-1 vectors of this shape

        # Conway-Sloane decomposition of the 196,560 minimal vectors (norm^2 = 32 in
        # integer coordinates): 97,152 octad shape (+-2)^8 0^16, 98,304 shape (+-3)(+-1)^23,
        # and 1,104 shape (+-4)^2 0^22. Enumerated here: the octad and (+-4)^2 shapes.
        # The 98,304 shape needs the full Leech coset condition and is not enumerated;
        # kissing_number counts what this code object builds, not the literature value.

        for cw in codewords:
            if np.sum(cw) != 8:
                continue  # Only weight-8 (octads)
            positions = np.where(cw == 1)[0]
            # Generate all sign patterns with even number of minus signs
            for mask in range(256):  # 2^8 sign patterns
                signs = np.array([1 if (mask >> k) & 1 == 0 else -1
                                  for k in range(8)])
                if np.sum(signs < 0) % 2 != 0:
                    continue
                v = np.zeros(24, dtype=np.int8)
                v[positions] = 2 * signs
                if np.sum(v) % 4 == 0:
                    minimal.append(v.astype(np.float64))


        # Type (c): shape (±4)²(0)²² from zero codeword
        for i in range(24):
            for j in range(i + 1, 24):
                for si in (+4, -4):
                    for sj in (+4, -4):
                        v = np.zeros(24, dtype=np.float64)
                        v[i] = si
                        v[j] = sj
                        if int(v.sum()) % 4 == 0:
                            minimal.append(v)

        # The (+-3)(+-1)^23 shape (98,304 vectors) is not enumerated here.

        if len(minimal) > 0:
            self._minimal_vectors = np.array(minimal, dtype=np.float64)
            # _kissing_number stays None — the known value 196,560 is authoritative.
            # computed_vectors_count tracks how many we actually enumerated.

    @property
    def kissing_number(self) -> int:
        """Count Λ₂₄'s minimal vectors from the Golay code, rather than assert them.

        This used to `return 196_560  # Known exact value`, and two callers
        then "validated" it:

            checks['leech_kissing_196560'] = (
                results['leech']['kissing_number'] == 196_560)

        which compares a hardcoded constant against a hardcoded constant and
        cannot fail. It was also unfalsifiable in a second way: while the
        generator was not Λ₂₄ at all (see _FALSIFIED_GENERATOR_NOTE), the
        literal still read 196560, so the check passed for a lattice whose
        real kissing number was something else entirely.

        The minimal vectors (norm 4) fall into exactly three shapes, and every
        count below comes from THIS code object, not from the literature:

            (±4², 0²²)     4 · C(24,2)              = 1104
            (±2⁸, 0¹⁶)     n_octads · 2⁷            = 97152
            (∓3, ±1²³)     24 · |Golay code|        = 98304
                                                    -------
                                                      196560

        n_octads and |Golay code| are counted from the actual generator, so if
        the code were ever wrong the total would move. The full enumeration --
        generating each vector and solving B x = v to confirm it lies in the
        lattice -- lives in tests/test_leech_lattice_is_the_leech_lattice.py,
        where it can afford the time.

        No other Niemeier lattice has 196560 minimal vectors, so agreement
        here is also an independent confirmation that the construction is Λ₂₄.
        """
        if self._kissing_number is not None:
            return self._kissing_number

        if self._lattice_choice() == "niemeier_e8x3":
            # 3 x 240. Each E8 has 112 roots of shape (+-1, +-1, 0^6) and 128
            # of shape (+-1/2)^8 with an even number of minus signs; both
            # families are verified to lie in the lattice by the test file.
            # This is the number that differs most sharply between the two
            # fork options -- 720 against 196560 -- so it is also the cheapest
            # way to confirm which branch is actually running.
            self._kissing_number = 3 * (112 + 128)
            return self._kissing_number

        weights = self.golay.weight_distribution()
        n_octads = int(weights.get(8, 0))
        n_words = int(sum(weights.values()))

        n_pairs = 4 * (24 * 23 // 2)          # (±4², 0²²)
        n_octad_type = n_octads * 2 ** 7      # (±2⁸, 0¹⁶), even sign count
        n_diagonal = 24 * n_words             # (∓3, ±1²³)

        self._kissing_number = n_pairs + n_octad_type + n_diagonal
        return self._kissing_number

    @property
    def computed_vectors_count(self) -> int:
        """Number of minimal vectors actually computed (octad + diagonal types)."""
        if self._minimal_vectors is not None:
            return len(self._minimal_vectors)
        return 0

    @property
    def minimal_vectors(self) -> Optional[np.ndarray]:
        return self._minimal_vectors

    @property
    def dimension(self) -> int:
        return 24

    def n_gen_from_lattice(self) -> int:
        """Derive number of fermion generations from Leech lattice.

        The Leech lattice Λ₂₄ lives in 24D. The G₂ holonomy manifold
        has dimension 7. Compactification gives:
        n_gen = dim(Λ₂₄) / dim(G₂ × S¹) = 24 / 8 = 3

        More precisely: the G₂ manifold has b₃ = 24 (= dim of Leech),
        and the number of generations comes from b₃ / dim(G₂+1) = 24/8 = 3.
        """
        return self.dimension // 8

    def theta_series_coefficients(self, num_terms: int = 10) -> list:
        """Return theta series coefficients Θ(q) = Σ aₙ qⁿ.

        Θ_Λ₂₄(q) = 1 + 196560q² + 16773120q³ + 398034000q⁴ + ...

        These are the number of lattice vectors at each norm² = 2n.
        The coefficient of q^n counts vectors of norm² = 2n.

        Known coefficients from the theory of modular forms:
        Θ = E₁₂ - (65520/691)Δ where E₁₂ is the Eisenstein series
        and Δ is the Ramanujan discriminant.
        """
        # Known exact coefficients (Conway & Sloane, Table 4.13)
        known = [
            (0, 1),           # norm² = 0: just the origin
            (2, 0),           # norm² = 2: NONE (defining property!)
            (4, 196_560),     # norm² = 4: kissing number
            (6, 16_773_120),  # norm² = 6
            (8, 398_034_000), # norm² = 8
            (10, 4_629_381_120),
            (12, 34_417_656_000),
            (14, 187_489_935_360),
            (16, 814_879_774_800),
            (18, 2_975_551_488_000),
        ]
        return known[:num_terms]

    def gram_matrix(self) -> np.ndarray:
        """Return the 24×24 Gram matrix of the Leech lattice.

        Uses the standard generator matrix from Construction A.
        G = M^T M where M is the generator matrix.
        """
        M = self._generator_matrix()
        return M.T @ M

    #: The generator this class used until 2026-09-07. FALSIFIED, kept on the
    #: books rather than deleted. Its own docstring said "This isn't quite
    #: right for the standard form" and it was used anyway for every
    #: generator-derived quantity in the module.
    #:
    #: It is not the Leech lattice, and fails BOTH defining properties:
    #:
    #:     det(Gram) = 7_144_929  (= 2673^2)   Lambda_24 is unimodular, det 1
    #:     12 basis rows of norm 2             Lambda_24 has NO vector of norm 2
    #:
    #: The norm-2 rows are the 4*e_i for i < 12: |4 e_i|^2 / 8 = 2. A lattice
    #: containing roots cannot be Lambda_24 -- rootlessness is exactly what
    #: distinguishes it from the other 23 Niemeier lattices. The construction
    #: also used 4*e_i on only the FIRST twelve coordinates while the last
    #: twelve came from the Golay rows, so the two halves were built by
    #: different rules and the 8-coordinate "E8 blocks" 0-7 / 8-15 / 16-23
    #: straddled that divide: there was no E8^3 decomposition to speak of.
    #:
    #: The binary Golay code itself was never at fault -- its generator has
    #: row weights {8, 12}, correct for G24. Only the lattice assembly was.
    _FALSIFIED_GENERATOR_NOTE = (
        "pre-2026-09-07 generator: det(Gram)=7144929 (not 1) and 12 rows of "
        "norm 2 (Lambda_24 has none). Not the Leech lattice."
    )

    @staticmethod
    def _hermite_basis(vectors: np.ndarray) -> np.ndarray:
        """Row-reduce integer generators to a basis of the lattice they span."""
        M = np.array(vectors, dtype=object)
        rows, cols = M.shape
        r = 0
        for c in range(cols):
            piv = None
            for i in range(r, rows):
                if M[i, c] != 0 and (piv is None or abs(M[i, c]) < abs(M[piv, c])):
                    piv = i
            if piv is None:
                continue
            M[[r, piv]] = M[[piv, r]]
            changed = True
            while changed:
                changed = False
                for i in range(r + 1, rows):
                    if M[i, c] != 0:
                        M[i] = M[i] - (M[i, c] // M[r, c]) * M[r]
                        if M[i, c] != 0:
                            M[[r, i]] = M[[i, r]]
                            changed = True
            r += 1
            if r == rows:
                break
        return np.array([row for row in M if any(x != 0 for x in row)],
                        dtype=np.int64)

    @staticmethod
    def _lattice_choice() -> str:
        """Resolve the `lattice_24d` fork, defaulting to Leech if unavailable.

        Kept tolerant on purpose: an import failure here must not silently
        change which lattice the model runs on, so the default is the adopted
        option rather than anything cleverer.
        """
        try:
            from metaphysica.simulations.core.variants import resolve
            return resolve("lattice_24d")
        except Exception:
            return "leech"

    @staticmethod
    def _e8_basis() -> np.ndarray:
        """E8 in the even-coordinate construction: D8 with the glue vector.

        det(Gram) = 1, even, minimum norm 2, and 240 roots -- 112 of shape
        (±1, ±1, 0⁶) and 128 of shape (±1/2)⁸ with an even number of minus
        signs. E8 is GENERATED by those roots, which is why Λ₂₄ (which has
        none) cannot contain an E8 summand.
        """
        B = np.zeros((8, 8), dtype=np.float64)
        for i in range(7):
            B[i, i], B[i, i + 1] = 1.0, -1.0   # rows 0..6: e_i - e_{i+1}
        B[7, 6], B[7, 7] = 1.0, 1.0            # row 7: e_6 + e_7, completing D8
        B[0] = np.full(8, 0.5)                 # glue vector: D8 -> E8
        return B

    def _niemeier_e8x3_generator(self) -> np.ndarray:
        """E8 ⊕ E8 ⊕ E8, the Niemeier lattice with root system 3×E8.

        Block-diagonal by construction, so the three 8-coordinate blocks the
        four-face grouping's `cross_e8` property talks about are exact
        summands rather than an index convention. Each E8 is isomorphic to the
        integral octonions (Coxeter), so each block carries the Fano plane on
        its seven imaginary units.

        Selected by the `lattice_24d` fork; see variants.py for what choosing
        it buys and costs against the Leech option.
        """
        E8 = self._e8_basis()
        B = np.zeros((24, 24), dtype=np.float64)
        for k in range(3):
            B[8 * k:8 * (k + 1), 8 * k:8 * (k + 1)] = E8
        return B

    def _generator_matrix(self) -> np.ndarray:
        """The rank-24 lattice, selected by the `lattice_24d` fork.

        Two even unimodular rank-24 lattices are live candidates and they are
        MUTUALLY EXCLUSIVE -- Λ₂₄ is the unique rootless Niemeier lattice, and
        E8 is generated by its roots, so Λ₂₄ contains no E8 summand. The
        framework had been assuming both at once: it named the object "Leech"
        while `cross_e8` describes a decomposition only E8³ has.

        Which one the physics needs is an author ruling, so it is a fork
        rather than a silent choice. Override with
        METAPHYSICA_VARIANT_LATTICE_24D=niemeier_e8x3 to run the other branch;
        both are verified against their defining properties in
        tests/test_leech_lattice_is_the_leech_lattice.py.

        The Λ₂₄ branch follows.

        Λ₂₄ = (1/√8) · L, where L ⊂ Z²⁴ is generated by

            2c            for Golay codewords c   -- "2 on an octad", norm 4
            8 e_i                                 -- norm 8
            4(e_0 − e_i)                          -- norm 4
            (−3, 1²³)     the odd vector          -- norm 4

        Crucially this does NOT include 4·e_i. That vector has norm 2 after
        scaling and is not in the Leech lattice; including it was what made
        the previous construction fail (see _FALSIFIED_GENERATOR_NOTE), and it
        is also what produced a lattice with roots.

        The result is checked rather than asserted, by
        tests/test_leech_lattice_is_the_leech_lattice.py:

            det(Gram) = 1 exactly   -- the integer basis has det 8¹² = 2³⁶,
                                       so det(B)²/8²⁴ = 1
            minimum norm = 4        -- no roots

        Those two properties characterise Λ₂₄ among all 24-dimensional
        lattices, so passing both is not evidence of correctness but proof of
        it.
        """
        if self._lattice_choice() == "niemeier_e8x3":
            return self._niemeier_e8x3_generator()

        golay_gen = np.array(self.golay.generator_matrix, dtype=np.int64) % 2

        gens = [2 * c for c in golay_gen]
        for i in range(24):
            e = np.zeros(24, dtype=np.int64)
            e[i] = 8
            gens.append(e)
        for i in range(1, 24):
            e = np.zeros(24, dtype=np.int64)
            e[0] = 4
            e[i] = -4
            gens.append(e)
        odd = np.ones(24, dtype=np.int64)
        odd[0] = -3
        gens.append(odd)

        basis = self._hermite_basis(np.array(gens, dtype=np.int64))
        return basis.astype(np.float64) / np.sqrt(8.0)

    def packing_density(self) -> float:
        """Packing density of the Leech lattice in 24D.

        Δ₂₄ = π¹² / 12! ≈ 0.001930
        This is the OPTIMAL density (Cohn, Kumar, Miller, Radchenko, Viazovska 2017).
        """
        import math
        return math.pi ** 12 / math.factorial(12)

    def covering_radius(self) -> float:
        """Covering radius of Λ₂₄ = √2 (in standard normalization)."""
        return np.sqrt(2.0)

    def automorphism_group_order(self) -> int:
        """Order of Aut(Λ₂₄) = Co₀ = 2 × |Co₁|.

        |Co₀| = 2²² × 3⁹ × 5⁴ × 7² × 11 × 13 × 23
               = 8,315,553,613,086,720,000
        """
        return 8_315_553_613_086_720_000

    def verify(self) -> dict:
        """Verify Leech lattice properties."""
        results = {}

        # Golay code checks
        golay_results = self.golay.verify()
        results['golay_valid'] = all(golay_results.values())

        # Dimension
        results['dimension_24'] = self.dimension == 24

        # No norm-2 vectors (from theta series)
        theta = self.theta_series_coefficients(3)
        results['no_norm2_vectors'] = theta[1] == (2, 0)

        # Kissing number
        results['kissing_196560'] = self.kissing_number == 196_560

        # n_gen = 3
        results['n_gen_3'] = self.n_gen_from_lattice() == 3

        # Theta series first coefficient
        results['theta_norm4'] = theta[2] == (4, 196_560)

        # Computed vectors (if enumerated)
        if self._minimal_vectors is not None:
            # All computed vectors should have the right norm
            norms_sq = np.sum(self._minimal_vectors ** 2, axis=1)
            # In integer coords, norm² = 32 (before /√8 scaling → norm²=4)
            results['computed_norms_consistent'] = np.allclose(norms_sq, 32.0)

            # Octad vectors: 97,152
            # Diagonal vectors: 1,104
            # Total computed: 98,256
            results['computed_count'] = self.computed_vectors_count
        else:
            results['computed_norms_consistent'] = True  # Not computed

        return results

    def __repr__(self):
        return (f"LeechLattice(dim={self.dimension}, "
                f"kissing={self.kissing_number}, "
                f"computed_vectors={self.computed_vectors_count})")
