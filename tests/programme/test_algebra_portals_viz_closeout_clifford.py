"""L6 close-out, clifford_unification: XA-02 (FALSIFIED description from run()),
XA-03 (\\texttt kept its backslash), XA-06 (section text follows run())."""
from metaphysica.simulations.PM.algebra import clifford_unification as cu

BOOST = "algebra.clifford_boost_conservation"


def _sim():
    return cu.CliffordUnificationSimulation()


def _patched_run(sim, monkeypatch, **changes):
    real = sim.run(None)
    real.update(changes)
    monkeypatch.setattr(sim, "run", lambda registry: dict(real))
    return real


def test_falsified_description_is_built_from_run(monkeypatch):
    sim = _sim()
    _patched_run(sim, monkeypatch, **{BOOST: 0.777})
    desc = next(p for p in sim.get_output_param_definitions() if p.path == BOOST).description
    assert "Computed 0.777" in desc and "0.408" not in desc


def test_minkowski_row_starts_with_texttt():
    rows = next(b for b in _sim().get_section_content().content_blocks if b.type == "table").rows
    row = next(r for r in rows if r[0].startswith("Minkowski interval"))
    assert row[1].startswith("\\texttt{")


def test_section_text_follows_a_changed_run(monkeypatch):
    sim = _sim()
    _patched_run(sim, monkeypatch, **{"algebra.clifford_g2_invariant": 0.5,
                                       "algebra.clifford_rotation_check": 0.25,
                                       "_checks_passed": 1, "_checks_total": 5,
                                       "_all_pass": False})
    blocks = sim.get_section_content().content_blocks
    callout = next(b for b in blocks if b.type == "callout")
    assert callout.title.startswith("Validation: 1/5 checks passed ~")
    assert "G₂ invariant = 0.5" in callout.content
    assert "Rotation error = 2.50e-01" in callout.content
    assert callout.callout_type == "info"
