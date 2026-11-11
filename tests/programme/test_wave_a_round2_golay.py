"""Wave A round 2, qec_golay_bridge. R2-10: paper_section is split into block helpers of 60
lines or fewer and builds the same section. R2-11: the metadata title states the computed
classification of the n = b3 identification (MISMATCH on the path in force)."""
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
    "_section_abstract",
    "_code_blocks",
    "_assessment_block",
    "_prediction_blocks",
)
# Measured 2026-11-11 from the 90-line paper_section before the split (file at commit f0ed6e8,
# tree at 0da8c5e): sha256 of json.dumps(dataclasses.asdict(section), sort_keys=True,
# ensure_ascii=True, default=str) under each forced b3 seed.
SECTION_SHA256_BEFORE_SPLIT = {
    "seed_43_joyce": "a6e055ce54670bf05ff9733ef9dff25135e39f926e77e686a79ecb1c0ab4dbb5",
    "seed_24": "fd56221a57f8efad07c54a606f317fb7d5aab0730be9bb4c847691313f633685",
}
CLASS_BY_SEED = {"seed_43_joyce": "MISMATCH", "seed_24": "MOTIVATED_IDENTIFICATION"}


def _section_digest(section) -> str:
    blob = json.dumps(dataclasses.asdict(section), sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


@pytest.mark.parametrize("name", SECTION_BUILDERS)
def test_section_builders_are_60_lines_or_fewer(name):
    source = inspect.getsource(getattr(q.QECGolayBridge, name))
    assert len(source.splitlines()) <= MAX_LINES, name


@pytest.mark.parametrize("seed", sorted(SECTION_SHA256_BEFORE_SPLIT))
def test_section_content_is_unchanged_by_the_split(seed):
    sim = q.QECGolayBridge()
    with selection.forced({"b3_seed": seed}):
        section = sim.paper_section()
    assert [b.type for b in section.content_blocks] == [
        "paragraph", "formula", "paragraph", "callout", "formula", "paragraph",
    ]
    assert _section_digest(section) == SECTION_SHA256_BEFORE_SPLIT[seed]


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
