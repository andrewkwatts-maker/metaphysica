"""Tests for the EML render-validity classifier.

WHY THIS EXISTS
---------------
The generator guarded parse-time failures and then accepted any non-None
render. ``"<parse error: invalid syntax (<unknown>, line 2)>"`` is not None,
so twelve formulas published that error string as their EML rendering while
the build counted them as successes.

These tests defend the replacement, and -- more importantly -- defend the
policy decision. The strict/permissive choice was made by running both
against the live formula set; the cases that decided it are pinned here, so
a future loosening has to consciously accept publishing "8" as the EML form
of "G_2 = Aut(O)".
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from metaphysica.generators.eml_render_validity import (
    REASON_OK,
    classify_eml_description,
    classify_render,
    classify_source,
    resolve_require_operator,
    tree_operator_count,
)


def _renders(latex="a + b", html="<div class='eml-flow'><svg><text/></svg></div>"):
    return {"latex": latex, "html": html}


_OP_TREE = ["add", "c", ["1", "#"], ["2", "#"]]
_LEAF_TREE = ["1", "#"]


# ── the defect that shipped ──────────────────────────────────────────────────


def test_error_text_is_not_content():
    """The exact string twelve formulas published to the website."""
    bad = _renders(latex="<parse error: invalid syntax (<unknown>, line 2)>")
    ok, reason = classify_render(bad, _OP_TREE)
    assert ok is False
    assert "error message" in reason


@pytest.mark.parametrize("marker", ["Traceback", "NameError", "SyntaxError"])
def test_other_failure_text_is_caught_too(marker):
    ok, _ = classify_render(_renders(latex=f"{marker}: boom"), _OP_TREE)
    assert ok is False


def test_error_text_in_html_is_caught_even_when_latex_is_clean():
    """A clean latex must not vouch for a broken diagram."""
    ok, reason = classify_render(
        {"latex": "a + b", "html": "<div>parse error: bad</div>"}, _OP_TREE
    )
    assert ok is False
    assert "html" in reason


def test_unresolved_internal_name_is_withheld():
    ok, reason = classify_render(_renders(latex="b3_leaf"), _OP_TREE)
    assert ok is False
    assert "internal" in reason


def test_empty_and_missing_are_withheld():
    assert classify_render(_renders(latex="   "), _OP_TREE)[0] is False
    assert classify_render({"html": "<svg/>"}, _OP_TREE)[0] is False


# ── source diagnosis: name the cause, not the symptom ───────────────────────


_COMMENTED_W0 = (
    "# w0 derivation in EML operator tree:\n"
    "# w0 = ops.add(ops.neg(eml_scalar(1.0)), ops.inv(b3_leaf()))\n"
    "#    = ops.div(ops.neg(eml_scalar(23.0)), b3_leaf())"
)


def test_commented_out_source_is_diagnosed_by_cause():
    """The real cause of all twelve 'parse errors': the whole expression is
    a comment block. 'invalid syntax on line 2' sent readers hunting for a
    typo that does not exist."""
    ok, reason = classify_source(_COMMENTED_W0)
    assert ok is False
    assert "commented out" in reason
    assert "2 candidate expressions" in reason


def test_diagnosis_counts_candidates_so_the_author_can_choose():
    one = "# only = ops.mul(eml_scalar(2.0), eml_scalar(3.0))"
    ok, reason = classify_source(one)
    assert ok is False
    assert "1 candidate expression" in reason
    assert "2 candidate" not in reason


def test_diagnosis_refuses_to_pick_the_canonical_form():
    """Eleven of the twelve carry 2-6 alternative or intermediate forms.
    Choosing among them is an authoring decision, and the message must say
    so rather than the generator silently uncommenting one."""
    _, reason = classify_source(_COMMENTED_W0)
    assert "authoring decision" in reason
    assert "not chosen here" in reason


def test_commented_block_with_no_expression_is_reported_separately():
    ok, reason = classify_source("# just a note, no code here")
    assert ok is False
    assert "no recognisable ops.* call" in reason


def test_real_expression_passes_source_check():
    ok, reason = classify_source("ops.add(eml_scalar(1.0), eml_scalar(2.0))")
    assert ok is True and reason == REASON_OK


def test_expression_with_a_leading_comment_line_still_passes():
    """Only an ENTIRELY commented block is the defect. A comment above real
    code is normal, and rejecting it would withhold working diagrams."""
    ok, _ = classify_source(
        "# explanatory note\nops.add(eml_scalar(1.0), eml_scalar(2.0))"
    )
    assert ok is True


def test_empty_source_is_not_a_parse_error():
    ok, reason = classify_source("")
    assert ok is False
    assert "no EML expression" in reason


# ── the operator criterion (structural, not a tuned number) ─────────────────


def test_operator_count_distinguishes_relation_from_symbol():
    assert tree_operator_count(_OP_TREE) == 1
    assert tree_operator_count(_LEAF_TREE) == 0


def test_lone_symbol_is_withheld_under_strict_policy():
    ok, reason = classify_render(
        _renders(latex="8"), _LEAF_TREE, require_operator=True
    )
    assert ok is False
    assert "no operator" in reason


def test_permissive_policy_would_publish_the_misleading_render():
    """Pins what the rejected branch actually did.

    'G_2 = Aut(O)' rendering as the glyph '8' is the case that decided the
    policy. If this ever starts failing, the permissive branch has been
    resurrected and someone should re-read why it lost.
    """
    ok, reason = classify_render(
        _renders(latex="8"), _LEAF_TREE, require_operator=False
    )
    assert ok is True and reason == REASON_OK


def test_a_healthy_render_passes():
    ok, reason = classify_render(_renders(), _OP_TREE)
    assert ok is True
    assert reason == REASON_OK


def test_missing_tree_does_not_reject_everything():
    """If the compact encoder is unavailable the operator test must skip.

    Rejecting every formula because a helper import failed would hide the
    entire EML layer over an unrelated breakage.
    """
    ok, _ = classify_render(_renders(), None, require_operator=True)
    assert ok is True


# ── the shipped artifact ────────────────────────────────────────────────────


def _load_renders():
    """The PUBLISHED bundle, not the local scratch copy.

    The repo root has a gitignored AutoGenerated/ used as build scratch. It
    is not tracked and not shipped, so it can be arbitrarily stale -- an
    earlier version of this loader checked it first and cheerfully validated
    a three-day-old bundle that predated the fix. Order is: explicit
    METAPHYSICA_OUT, then the published site, then scratch as a last resort.
    """
    raw = os.environ.get("METAPHYSICA_OUT")
    candidates = []
    if raw:
        candidates.append(Path(raw) / "AutoGenerated" / "formula_renders.json")
    candidates += [
        Path("H:/Github/PrincipiaMetaphysica/AutoGenerated/formula_renders.json"),
        Path(__file__).resolve().parents[1] / "AutoGenerated" / "formula_renders.json",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        bundle = json.loads(path.read_text(encoding="utf-8"))
        if "_policy" not in bundle:
            # Written by a generator older than this feature; it cannot be
            # judged against a policy it never applied. Skipping is honest;
            # failing would blame the artifact for the build being stale.
            continue
        return bundle
    pytest.skip(
        "no formula_renders.json carrying a _policy block; regenerate with "
        "python -m metaphysica.generators.generate_formula_renders"
    )


def test_no_published_render_contains_error_text():
    """The regression that matters: nothing shipped may be an error string."""
    bundle = _load_renders()
    offenders = [
        fid for fid, entry in bundle["f"].items()
        for value in entry.values()
        if "parse error" in str(value).lower()
    ]
    assert not offenders, f"error text published as EML content: {offenders}"


def test_withheld_formulas_are_recorded_with_reasons():
    """Omission must be auditable, not silent -- otherwise this is the same
    class of defect as the curated allowlist that hid the H0 conflicts."""
    bundle = _load_renders()
    withheld = bundle.get("_unrenderable", {})
    assert withheld, "expected some withheld formulas; none recorded"
    for fid, reason in withheld.items():
        assert reason and len(reason) > 12, f"{fid} withheld with no reason"
        assert fid not in bundle["f"], f"{fid} both withheld and published"


def test_policy_is_recorded_in_the_artifact():
    """The artifact must record the policy that was ENFORCED.

    This asserted ``is True`` against a hardcoded literal while the
    generator wrote the REQUIRE_OPERATOR module constant and
    classify_render separately resolved render_policy from the variant
    registry. Nothing tied the two together, so the assertion held no
    matter which policy the build actually applied -- it could not fail.
    Comparing against the resolved value is what makes it a check.
    """
    bundle = _load_renders()
    recorded = bundle.get("_policy", {}).get("require_operator")
    assert recorded is resolve_require_operator(), (
        f"artifact records require_operator={recorded} but the resolved "
        f"policy is {resolve_require_operator()}"
    )


# ── the all-fail tripwire ───────────────────────────────────────────────────


def _write_formulas(dirpath, formulas):
    ag = dirpath / "AutoGenerated"
    ag.mkdir(parents=True, exist_ok=True)
    (ag / "formulas.json").write_text(
        json.dumps({"formulas": formulas}), encoding="utf-8"
    )
    return ag


def test_tripwire_fires_when_every_render_is_unshowable(tmp_path, monkeypatch):
    """A broken renderer must fail the build, not publish an empty bundle.

    Individual formulas legitimately have no EML form. Every one failing
    means eml-math itself is broken, and a silently empty bundle would ship
    a site with no EML anywhere while the build stayed green.
    """
    from metaphysica.generators import generate_formula_renders as g

    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    _write_formulas(tmp_path, {
        "a": {"eml_tree_str": "ops.add(eml_scalar(1.0), eml_scalar(2.0))"},
        "b": {"eml_tree_str": "ops.mul(eml_scalar(3.0), eml_scalar(4.0))"},
    })
    monkeypatch.setattr(g, "classify_render", lambda *a, **k: (False, "forced"))
    assert g.main([]) == 1, "all-fail must exit non-zero"


def test_tripwire_does_not_fire_on_a_healthy_run(tmp_path, monkeypatch):
    """The other half of the mutation: the tripwire must be specific.

    A gate that always fires is as useless as one that never does.
    """
    from metaphysica.generators import generate_formula_renders as g

    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    ag = _write_formulas(tmp_path, {
        "a": {"eml_tree_str": "ops.add(eml_scalar(1.0), eml_scalar(2.0))"},
    })
    assert g.main([]) == 0
    bundle = json.loads((ag / "formula_renders.json").read_text(encoding="utf-8"))
    assert "a" in bundle["f"]


def test_a_single_bad_formula_does_not_fail_the_build(tmp_path, monkeypatch):
    """Withholding one formula is normal; only total failure is fatal."""
    from metaphysica.generators import generate_formula_renders as g

    monkeypatch.setenv("METAPHYSICA_OUT", str(tmp_path))
    ag = _write_formulas(tmp_path, {
        "good": {"eml_tree_str": "ops.add(eml_scalar(1.0), eml_scalar(2.0))"},
        "bare": {"eml_tree_str": "eml_scalar(8.0)"},
    })
    assert g.main([]) == 0
    bundle = json.loads((ag / "formula_renders.json").read_text(encoding="utf-8"))
    assert "good" in bundle["f"]
    assert "bare" in bundle["_unrenderable"]
    assert "no operator" in bundle["_unrenderable"]["bare"]


# ── display normalisation of internal leaf names ────────────────────────────


def test_leaf_marker_is_stripped_and_subscripted():
    """b3_leaf() is metaphysica's spelling for the b3 leaf, not an eml-math
    builtin, so the parser labelled the node verbatim and every renderer
    printed it -- 'b3_leaf' was visible in 92 published formula renders."""
    from metaphysica.generators.eml_render_validity import normalise_leaf_names

    assert normalise_leaf_names("b3_leaf()") == "b_3"
    assert normalise_leaf_names(
        "ops.div(eml_scalar(144.0), ops.mul(eml_scalar(2.0), b3_leaf()))"
    ) == "ops.div(eml_scalar(144.0), ops.mul(eml_scalar(2.0), b_3))"


def test_leaf_without_an_index_keeps_its_stem():
    from metaphysica.generators.eml_render_validity import normalise_leaf_names

    assert normalise_leaf_names("chi_leaf()") == "chi"


def test_normalisation_leaves_real_operators_alone():
    """It must not eat ops.* calls or non-empty argument lists."""
    from metaphysica.generators.eml_render_validity import normalise_leaf_names

    expr = "ops.add(eml_scalar(1.0), eml_pi())"
    out = normalise_leaf_names(expr)
    assert "ops.add(" in out and "eml_scalar(1.0)" in out


def test_no_published_render_leaks_an_internal_leaf_name():
    """The regression, checked against the shipped bundle."""
    import re

    bundle = _load_renders()
    offenders = [
        fid for fid, entry in bundle["f"].items()
        for value in entry.values()
        if re.search(r"\b[A-Za-z0-9]+_leaf\b", str(value))
    ]
    assert not offenders, f"internal *_leaf names published: {offenders[:6]}"


# ── which eml_descriptions may be offered as an EML option ──────────────────
#
# Pages/parameters.html attached the Normal|EML pill on "eml_description is
# non-empty" alone, so 53 parameters offered an EML tab that showed prose, a
# bare undefined tally, or a call to an operator eml-math does not define.


def test_prose_is_not_offered_as_an_eml_option():
    ok, reason, cat = classify_eml_description(
        "Integer count of the 72 gates that returned PASS status."
    )
    assert ok is False
    assert cat == "prose"
    assert "prose" in reason


def test_a_real_expression_is_offered():
    ok, reason, cat = classify_eml_description(
        "EML: ops.div(eml_scalar(144.0), eml_scalar(24.0)) - chi/b3"
    )
    assert ok is True and cat == "ok" and reason == REASON_OK


def test_literal_echo_is_offered_even_though_it_has_no_operator():
    """The distinction the operator count alone gets wrong.

    An earlier draft suppressed every operator-free expression and withheld
    175 working options -- CODATA echoes like this one -- to catch the 10
    undefined placeholders below.
    """
    ok, _, cat = classify_eml_description(
        "EML: eml_scalar(137.035999177) - CODATA 2022 alpha inverse",
        context={},
    )
    assert ok is True and cat == "ok"


def test_undefined_tally_with_no_operator_is_withheld():
    ok, reason, cat = classify_eml_description(
        "EML: eml_scalar(N_pass) - count of LOCKED gates passing",
        context={"b3": 24.0},
    )
    assert ok is False and cat == "no_relation"
    assert "N_pass" in reason


def test_operator_eml_math_does_not_provide_is_withheld_and_named():
    ok, reason, cat = classify_eml_description(
        "EML: ops.quadratic(eml_vec('g2_multivector'), eml_signature('+++'))",
        operators=frozenset({"add", "mul", "div"}),
    )
    assert ok is False and cat == "not_expressible"
    assert "ops.quadratic" in reason and "eml_signature" in reason


def test_indexed_family_comprehension_is_withheld():
    ok, reason, cat = classify_eml_description(
        "EML: ops.sqrt(ops.sum(ops.pow(eml_vec('d'), eml_scalar(2.0)) "
        "for i in range(27)))",
        operators=frozenset({"sqrt", "sum", "pow"}),
    )
    assert ok is False and cat == "not_expressible"
    assert "indexed-family" in reason


def test_an_expression_with_an_unregistered_operand_is_still_offered():
    """Deliberate: depicting a relation is the bar, not evaluating.

    ops.div(V_cb, lambda_W**2) is a readable statement of how A is built
    even when lambda_W is in no registry. Withholding it would hide a
    genuine registry gap behind a missing UI control, and the cross-check
    already reports it as an unevaluable row.
    """
    ok, _, cat = classify_eml_description(
        "EML: ops.div(V_cb, ops.pow(lambda_W, eml_scalar(2.0)))",
        context={},
    )
    assert ok is True and cat == "ok"


def test_missing_eml_math_does_not_withhold_everything():
    """Fail-open: an empty operator surface must not suppress the site."""
    ok, _, cat = classify_eml_description(
        "EML: ops.quadratic(eml_vec('v'), eml_scalar(1.0))",
        operators=frozenset(),
    )
    assert ok is True and cat == "ok"


def _load_offer_policy():
    """The published EML offer policy, same search order as _load_renders."""
    raw = os.environ.get("METAPHYSICA_OUT")
    candidates = []
    if raw:
        candidates.append(Path(raw) / "AutoGenerated" / "eml_offer_policy.json")
    candidates += [
        Path("H:/Github/PrincipiaMetaphysica/AutoGenerated/eml_offer_policy.json"),
        Path(__file__).resolve().parents[1] / "AutoGenerated" / "eml_offer_policy.json",
    ]
    for path in candidates:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    pytest.skip(
        "no eml_offer_policy.json; regenerate with "
        "python -m metaphysica.generators.eml_param_crosscheck"
    )


def test_every_withheld_parameter_is_recorded_with_a_reason_and_category():
    """Suppression must be auditable, not silent -- the same requirement
    already placed on withheld formula diagrams."""
    policy = _load_offer_policy()
    withheld = policy.get("_unrenderable", {})
    categories = policy.get("_categories", {})
    assert withheld, "expected some withheld parameters; none recorded"
    for path, reason in withheld.items():
        assert reason and len(reason) > 12, f"{path} withheld with no reason"
        assert path in categories, f"{path} withheld with no category"
        assert categories[path] in {
            "prose", "malformed", "no_relation", "not_expressible",
        }, f"{path} has unknown category {categories[path]!r}"


def test_suppression_stays_a_minority_of_the_offered_set():
    """A tripwire, not a quality bar.

    The first draft of classify_eml_description suppressed on operator count
    alone and withheld 246 of 641 -- it stripped every CODATA echo. Nothing
    caught it but reading the list. If suppression ever exceeds the offered
    count again, the classifier has broken, not the data.
    """
    policy = _load_offer_policy()
    withheld = len(policy.get("_unrenderable", {}))
    offered = policy.get("_offered_count", 0)
    assert offered > withheld, (
        f"{withheld} parameters withheld vs {offered} offered -- the "
        f"classifier is suppressing valid expressions"
    )
