"""The top-down overview: one generated story for the abstract and main page.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from metaphysica.simulations.PM.geometry.closed_geometry.overview import (
    LAYER_ORDER,
    MARK_BEGIN,
    MARK_END,
    inject,
    layers,
    overview_html,
    pretty,
)


def test_the_layers_come_in_the_registered_order():
    assert [layer["key"] for layer in layers()] == list(LAYER_ORDER)


def test_every_layer_has_a_title_and_a_lead():
    for layer in layers():
        assert layer["title"].strip() and layer["lead"].strip(), layer["key"]


def test_the_typesetting_never_double_escapes():
    text = " ".join(it for layer in layers()
                    for it in layer["items"] + [layer["lead"]])
    assert "&&" not in text and ";;" not in text
    assert pretty("pi_1 and chi_eff and chi") == (
        "&pi;<sub>1</sub> and &chi;<sub>eff</sub> and &chi;")


def test_unverified_standard_rows_are_not_rendered_as_cited():
    from metaphysica.simulations.PM.geometry.closed_geometry.provenance import (
        by_kind,
    )

    standard = {layer["key"]: layer for layer in layers()}["standard"]
    unverified = [p for p in by_kind("STANDARD") if not p.verified]
    assert len(standard["items"]) == len(by_kind("STANDARD")) - len(unverified)


def test_the_selection_layer_follows_the_switches(monkeypatch):
    def selection():
        return " ".join({layer["key"]: layer for layer in layers()}[
            "selection"]["items"])

    monkeypatch.delenv("METAPHYSICA_VARIANT_G2_FORM_CONVENTION", raising=False)
    monkeypatch.delenv("METAPHYSICA_VARIANT_SEED_SELECTION", raising=False)
    adopted = selection()
    assert "active path" in adopted and "WA-1, adopted" in adopted

    monkeypatch.setenv("METAPHYSICA_VARIANT_G2_FORM_CONVENTION", "all_plus_one")
    assert "&pi;<sub>1</sub> alone" in selection()

    monkeypatch.setenv("METAPHYSICA_VARIANT_SEED_SELECTION", "ruling_only")
    assert "2026-09-22 ruling" in selection()


def test_inject_replaces_only_the_marked_block(tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<p>before</p>%s\nSTALE-BLOCK-SENTINEL\n%s<p>after</p>"
                    % (MARK_BEGIN, MARK_END), encoding="utf-8")
    assert inject(page)
    text = page.read_text(encoding="utf-8")
    assert text.startswith("<p>before</p>") and text.endswith("<p>after</p>")
    assert "STALE-BLOCK-SENTINEL" not in text
    assert 'id="theory-at-a-glance"' in text
    assert text.count(MARK_BEGIN) == 1 and text.count(MARK_END) == 1


def test_a_page_without_markers_is_left_alone(tmp_path):
    page = tmp_path / "index.html"
    page.write_text("<p>no markers</p>", encoding="utf-8")
    assert inject(page) is False
    assert page.read_text(encoding="utf-8") == "<p>no markers</p>"


def test_the_section_carries_the_live_seed():
    html = overview_html()
    assert "(12, 43)" in html
    assert html.startswith(MARK_BEGIN) and html.endswith(MARK_END)
