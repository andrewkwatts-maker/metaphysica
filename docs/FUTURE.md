# Future work: scaling the physics engine

This is a roadmap, not a commitment. Each phase names what must be **true**
before the next one starts, because the failure mode this document exists to
prevent is a fast implementation that quietly disagrees with the slow one.

---

## Governing rule: CPU is ground truth until parity is proven

Every acceleration phase below must reproduce the CPU reference **exactly**
(bitwise where the operation is exact, to a stated tolerance where it is not)
before any CPU routine is deprecated. Not "close enough", not "within
tolerance on the cases we tried" — a cross-validation harness that runs both
implementations on the same inputs and fails on divergence.

This rule is written from experience. The EML numeric core carried a Rust and
a Python implementation of the same operation whose guards had drifted:
`OVERFLOW_THRESHOLD` was the rounded literal `709.78` rather than
`f64::MAX.ln() = 709.782712893384`, and the frame-shift guard clamped negative
subnormals instead of flooring only exact zero. The same `EMLPoint` gave
different answers depending on whether it evaluated in Rust or Python — 6 of
10 probe cases diverged. Nothing detected it, because no harness compared the
two. **A second implementation without a parity harness is a second source of
truth.**

---

## Phase 1 — CPU reference (current)

Symbolic and double-precision NumPy implementations, correct by construction
and slow by acceptance.

| Component | Status |
|---|---|
| `exterior_algebra` — sparse `Form`, wedge, symbolic `exterior_d` | done |
| `shadow_clifford` — explicit Cl(12,1), 64×64 gammas | done |
| `topological_terms` — 7D flux, two independent routes | done |
| `exterior_degree_gate` — form-degree validation | done |
| `bridge_geometry` — moduli potential, scipy stabilisation | pre-existing |
| bridge-to-channel join — Fano triangles, rainbow labellings, K₄ closure, PSL(3,2) uniqueness | done (2026-09-01) |
| K₁₂ Eisenstein lattice / 729 vacua | not started |
| 26D → 13D boundary variation | not started |

**Exit criterion:** every component has a test that can fail, demonstrated by
mutation. Several already do — the wedge sign convention, the degree gate's
rejection, the RP gate's `MARGINAL_VACUOUS`.

---

## Phase 2 — Vectorised dispatch (PyTorch / JAX)

Vectorise across dimensions and use automatic differentiation to obtain
equations of motion, rather than hand-deriving them.

**Prerequisites:**
- Phase 1 exit criterion met for the component being ported.
- A parity harness *written before the port*, not after.

**The trap to avoid:** autodiff makes it cheap to differentiate the wrong
functional. The variational derivative must be checked against a finite
difference of the action on a case where the answer is known analytically —
otherwise a plausible gradient of a subtly wrong Lagrangian is
indistinguishable from a correct one.

**Sizing is not optional.** The dense-vs-sparse table in
`exterior_algebra.py` applies unchanged on GPU, and worse: a dense 7-form in
28D is 100.5 GB, and a 13D Levi-Civita is 2.2 PiB. GPU memory is *smaller*
than host memory, so every guard in `guard_form_size()` must be enforced on
the accelerated path too, not bypassed for speed.

---

## Phase 3 — CUDA kernels

Custom kernels for path-integral sampling across the 729 K₁₂ vacuum states.

**Hard gate:** 100% numerical parity against Phase 1 on the full test corpus,
including the edge cases — subnormals, exact zeros, and the degenerate
configurations (θ = 90° exactly, where `cos θ` is `6.12e-17` rather than `0`
and the metric channel is vacuous rather than absent). Those are precisely
where a fast path diverges, and precisely where the physics is interesting —
the topological channel is *maximal* at exactly that point, and cross-shadow
coupling is structurally unavoidable there (no placement of twelve bridges on
the cycle switches it off; the minimum live-coupling count is five, never zero).

Only after that gate may a CPU routine be marked deprecated — and even then
it stays in the tree as the reference the harness compares against.

---

## Deferred, with reasons

**Discrete exterior calculus on a compact G₂ manifold.** This is the right
long-term answer for genuine topological content, and the reason
`topological_terms.py` scopes its result to "the integrand is non-vanishing"
rather than claiming a topological invariant. Flat ℝ⁷ has trivial holonomy and
no non-trivial 7-cycles, so integration there is coefficient × volume. Getting
further needs harmonic representatives on a compact manifold with b₃ = 24.
Deferred because it is 600+ lines of mesh infrastructure that does not exist
anywhere in the tree, and because it unblocks nothing that is currently
blocked. Note the scope is **unchanged** by the bridge-to-channel join: that
result is combinatorial (Fano incidence of φ's associative triples) and would
hold on any G₂ structure with the same incidence, so it does not by itself
supply topological content. It is also **contingent on the TCS obstruction**
(b₂ + b₃ must be odd for a twisted connected sum; the claimed (4, 24) is even),
which remains open and is independent of the (24,2) signature ruling.

**Finite-difference exterior derivative.** Rejected outright, not deferred. At
n=13, p=3 with only 4 points per direction it needs 143 GB — the same shape as
the incident that took a machine down — and 4 points per direction is far too
coarse for a derivative to converge anyway. It would also demote `d² = 0` from
a theorem to a tolerance, which is the opposite of the direction this codebase
has been moving.

**Reviving the 16,763 dead lines.** Nine modules are imported under `V19`
names that do not exist; the guards swallow the `ImportError` and the modules
never run. `tests/test_no_silently_dead_imports.py` records them as a ratchet.
Switching them on is an author ruling rather than a typo fix: they carry
roughly 1,400 lines of `Formula` literals that would enter the paper the
moment the imports resolve.
