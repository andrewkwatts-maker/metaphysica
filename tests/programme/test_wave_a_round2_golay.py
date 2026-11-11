"""Wave A round 2, qec_golay_bridge. R2-10: paper_section is split into block helpers of 60
lines or fewer. R2-11: the metadata title states the computed classification of the n = b3
identification (MISMATCH on the path in force).

Review RQ (2026-11-11): the section title is built from the same classification; the clause
that says where the b3 numbers agree is built from the classification and types no path name;
the section states the classical Golay [24,12,8] and k = 0 as CSS, and the [[24,12,8]]
quantum-code claim carries no DERIVED label (the module's copy of audit finding paper-app-b-12)."""
import dataclasses
import hashlib
import inspect
import json

import pytest

from metaphysica.simulations.PM.algebra import qec_golay_bridge as q
from metaphysica.simulations.core.variants import selection

MAX_LINES = 60  # rule 9 of docs/plan/programme/FIX_BRIEFS.md
SECTION_BUILDERS = (
    "paper_section",
    "_match_scope",
    "_section_abstract",
    "_code_blocks",
    "_assessment_block",
    "_prediction_blocks",
)
# sha256 of json.dumps(dataclasses.asdict(section), sort_keys=True, ensure_ascii=True,
# default=str) under each forced b3 seed.
# Measured 2026-11-11 from paper_section after the three review RQ repairs listed above (the
# module of this commit, tree at b297023). They replace the digests measured the same day from
# the 90-line paper_section before the split (file at f0ed6e8, tree at 0da8c5e), which the split
# at 324319e reproduced:
# seed_43_joyce a6e055ce54670bf05ff9733ef9dff25135e39f926e77e686a79ecb1c0ab4dbb5 and
# seed_24 fd56221a57f8efad07c54a606f317fb7d5aab0730be9bb4c847691313f633685. Those two pinned the
# title "Quantum Error Correction from G2 Topology", the typed "off-path seed_24" and the
# "valid CSS quantum code [[24,12,8]] ... DERIVED" claim, which the repairs remove.
SECTION_SHA256 = {
    "seed_43_joyce": "04a13e7f487220a8f7114ab25600bd10f9e173b0f490edde97ee8edc983806ea",
    "seed_24": "5a933b642949b5dfe495fa83d0b64bd507ce96313fab7c0c82583bc910038b21",
}
CLASS_BY_SEED = {"seed_43_joyce": "MISMATCH", "seed_24": "MOTIVATED_IDENTIFICATION"}


def _section_digest(section) -> str:
    blob = json.dumps(dataclasses.asdict(section), sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def _section(seed):
    with selection.forced({"b3_seed": seed}):
        return q.QECGolayBridge().paper_section()


def _text(section) -> str:
    return " ".join([section.abstract] + [str(b.content) for b in section.content_blocks])


@pytest.mark.parametrize("name", SECTION_BUILDERS)
def test_section_builders_are_60_lines_or_fewer(name):
    source = inspect.getsource(getattr(q.QECGolayBridge, name))
    assert len(source.splitlines()) <= MAX_LINES, name


@pytest.mark.parametrize("seed", sorted(SECTION_SHA256))
def test_section_content_is_pinned_on_each_seed(seed):
    section = _section(seed)
    assert [b.type for b in section.content_blocks] == [
        "paragraph", "formula", "paragraph", "callout", "formula", "paragraph",
    ]
    assert _section_digest(section) == SECTION_SHA256[seed]


@pytest.mark.parametrize("seed", sorted(CLASS_BY_SEED))
def test_metadata_title_states_the_computed_classification(seed):
    sim = q.QECGolayBridge()
    with selection.forced({"b3_seed": seed}):
        computed = sim.get_mapping_table()[0]["classification"]
        title = sim.metadata.title
    assert computed == CLASS_BY_SEED[seed]
    assert f"({computed} on the path in force)" in title
    assert "b3 identification" in title
    assert "from G2 Topology" not in title


@pytest.mark.parametrize("seed", sorted(CLASS_BY_SEED))
def test_section_title_states_the_computed_classification(seed):
    title = _section(seed).title
    assert f"({CLASS_BY_SEED[seed]} on the path in force)" in title
    assert "b3 identification" in title
    assert "from G2 Topology" not in title


def test_match_scope_follows_the_classification_on_each_seed():
    mismatch, motivated = _text(_section("seed_43_joyce")), _text(_section("seed_24"))
    # On the path where the classification is MISMATCH the numbers agree elsewhere only.
    assert mismatch.count("only on seed_24, not on the path in force") == 2
    assert "does not support a link" in mismatch
    # On the path where they agree, the text does not call that path off-path.
    assert motivated.count("on this path as a numerical coincidence") == 2
    assert "not on the path in force" not in motivated
    assert "does not support a link" not in motivated
    assert "does not establish a link" in motivated
    for text in (mismatch, motivated):
        assert "off-path" not in text


@pytest.mark.parametrize("name", SECTION_BUILDERS)
def test_section_builders_type_no_path_name(name):
    source = inspect.getsource(getattr(q.QECGolayBridge, name))
    for path in q.PATHS:
        assert path not in source, (name, path)


def test_paths_with_b3_reads_the_declared_paths():
    assert q._paths_with_b3(24) == ["seed_24"]
    assert q._paths_with_b3(43) == ["seed_43_joyce"]
    with pytest.raises(ValueError):
        q._paths_with_b3(25)


def test_css_code_facts_give_k_zero_and_a_failed_singleton_bound():
    facts = q.QECGolayBridge().css_code_facts()
    assert (facts["n"], facts["k_classical"], facts["d"]) == (24, 12, 8)
    assert facts["stabilizer_generators"] == 24
    assert facts["k_css"] == 0
    assert (facts["singleton_lhs"], facts["singleton_rhs"]) == (12, 14)
    assert facts["quantum_claim_obeys_singleton"] is False


@pytest.mark.parametrize("seed", sorted(CLASS_BY_SEED))
def test_section_states_classical_golay_and_k_zero_as_css(seed):
    section = _section(seed)
    text = _text(section)
    assert "classical [24,12,8] code" in text
    assert "k = 0 logical qubits" in text
    assert "quantum Singleton bound n - k >= 2(d - 1) (12 < 14)" in text
    assert "DERIVED" not in text
    assert "valid CSS quantum code" not in text
    assert "encodes 12 logical qubits" not in text
    assert "[[24,12,8]] is withdrawn" in text
    formula = section.content_blocks[1]
    assert formula.formula_id == "css-code-parameters"
    assert "[[" not in formula.content
    assert formula.content.endswith("= 0")
