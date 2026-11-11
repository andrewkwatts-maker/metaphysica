"""L6 close-out, qec_golay_bridge XA-08: b3 and the classification in the text are computed
(MISMATCH on the adopted path), and the module is RETIRE-FROM-PAPER (rule 5)."""
from metaphysica.simulations.PM.algebra import qec_golay_bridge as q
from metaphysica.simulations.core.variants import selection


def _text(section):
    return " ".join([section.abstract] + [str(b.content) for b in section.content_blocks])


def test_section_text_follows_the_computed_classification():
    sim = q.QECGolayBridge()
    with selection.forced({"b3_seed": "seed_43_joyce"}):
        cls = sim.get_mapping_table()[0]["classification"]
        text = _text(sim.paper_section())
    assert cls == "MISMATCH"
    assert "is MISMATCH on the path in force" in text and "b3 = 43" in text
    assert "MOTIVATED_IDENTIFICATION" not in text
    with selection.forced({"b3_seed": "seed_24"}):
        text24 = _text(sim.paper_section())
    assert "is MOTIVATED_IDENTIFICATION on the path in force" in text24


def test_metadata_types_no_b3():
    desc = q.QECGolayBridge().metadata.description
    assert "43" not in desc and "b3 = 24" not in desc


def test_retired_from_paper_and_score_with_rows_kept():
    sim = q.QECGolayBridge()
    assert q.RETIRED_FROM_PAPER is True
    assert sim.get_section_content() is None
    assert sim.get_certificates() == []
    assert len(sim.qec_certificates()) == 4
    assert {p.path for p in sim.get_output_param_definitions()} == set(sim.output_params)
    assert {f.id for f in sim.get_formulas()} == set(sim.output_formulas)
