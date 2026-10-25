"""D-025 core paper: abstract and introduction limits, manifest, fixtures."""
import hashlib
import html
import json
import re
from pathlib import Path

import pytest

from metaphysica.generators import generate_core_paper as gen
from metaphysica.generators.refresh_paper_conclusions import _render
from metaphysica.simulations.PM.paper import core_text
from metaphysica.simulations.PM.paper.core_manifest import (
    CORE_MANIFEST, manifest_ids)

FIXTURE = Path(__file__).parent / "fixtures" / "old_introduction.json"


@pytest.fixture(scope="module")
def sections():
    sec, _ = _render(with_core_text=True)
    return sec


def _words(entry):
    return gen.section_words(entry)


def test_abstract_is_250_words_or_fewer(sections):
    assert 0 < _words(sections["0"]) <= 250


def test_introduction_is_900_words_or_fewer(sections):
    assert 0 < _words(sections["1"]) <= 900


def test_abstract_has_no_typed_number():
    template, vals = core_text.abstract_parts()
    text = template
    for key in vals:
        text = text.replace("{%s}" % key, "")
    text = html.unescape(re.sub(r"</?(sub|sup)>", "", re.sub(r"<(?!/?(sub|sup)>)[^>]+>", " ", text)))
    typed = re.findall(r"(?<![A-Za-z_])[0-9][0-9.,]*", text)
    assert typed == [], "typed numbers in the abstract: %s" % typed


def test_abstract_numbers_come_from_live_sources(sections):
    template, vals = core_text.abstract_parts()
    assert core_text.abstract_html() == template.format(**vals)
    block = sections["0"]["content_blocks"][0]["content"]
    assert block == core_text.abstract_html()


def test_manifest_ids_exist_in_sections(sections):
    assert 12 <= len(CORE_MANIFEST) <= 20
    for sid in ("0", "1", "2.4", "7"):
        assert sid in manifest_ids()
    sections_json = json.loads((gen.autogen_dir() / "sections.json")
                               .read_text(encoding="utf-8"))["sections"]
    assert [i for i in manifest_ids() if i not in sections_json] == []


def test_generator_fails_early_on_missing_id():
    with pytest.raises(SystemExit):
        gen.build({"0": {"title": "x", "content_blocks": []}})


def test_core_paper_json_matches_manifest(sections):
    path = gen.autogen_dir() / "core_paper.json"
    assert path.is_file(), "run generate_core_paper first"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert [c["id"] for c in data["core"]] == list(manifest_ids())
    assert [c["role"] for c in data["core"]] == [r for _, r in CORE_MANIFEST]
    core_ids = set(manifest_ids())
    assert not core_ids & {s["id"] for s in data["supplementary"]}
    t = data["totals"]
    assert t["all_words"] == t["core_words"] + t["supplementary_words"]


def test_extended_introduction_keeps_old_text(sections):
    ext = sections["extended-introduction"]
    assert "supplementary" in ext["title"].lower()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    blocks = json.dumps(ext["content_blocks"], sort_keys=True,
                        ensure_ascii=False)
    assert hashlib.sha256(blocks.encode("utf-8")).hexdigest() == \
        fixture["sha256"]
    assert len(ext["content_blocks"]) == fixture["n_blocks"]


def test_extended_abstract_keeps_the_layered_abstract():
    """D-025 demotes the pre-D-025 layered abstract; it must not be lost."""
    from metaphysica.simulations.PM.paper.abstract import AbstractExtendedV17_2

    sim = AbstractExtendedV17_2()
    sec = sim.get_section_content()
    labels = {b.label for b in sec.content_blocks}
    assert sec.section_id == "extended-abstract"
    assert {"abstract-research-status-notice", "abstract-lead",
            "abstract-predictions", "abstract-note"} <= labels
    assert sim.get_formulas() == [] and sim.get_gate_checks() == []
