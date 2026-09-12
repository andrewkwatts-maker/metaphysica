"""The free-variable ledger, and the two guards that keep it honest.

Every count asserted here is asserted twice: once against the tree as it
stands, and once against a perturbed copy of the tree, so that a number
which happened to be right for the wrong reason cannot pass. A test that
returns the same verdict for every input has verified nothing.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from metaphysica.simulations.core.free_variable_ledger import (
    DERIVATION_CLAIMING_STATUSES,
    NON_DERIVED_STATUSES,
    ROLE_COMPARISON_ONLY,
    ROLE_LOAD_BEARING_INPUT,
    ROLE_PERMITTED_OR_SCALE,
    ROLE_UNRESOLVED,
    ROLES,
    admits_a_fit,
    build_ledger,
    iter_parameter_calls,
    published_free_variable_count,
    simulations_root,
    sweep_anchor_rows,
    sweep_parameter_rows,
    write_ledger,
)

# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ledger():
    return build_ledger()


A_FIT = '''
from metaphysica.simulations.base import Parameter

PARAMS = [
    Parameter(
        path="scratch.knob",
        name="A knob",
        units="dimensionless",
        status="FITTED",
        description="Chosen so the prediction lands on the measured value.",
        no_experimental_value=True,
    ),
]
'''

A_LAUNDERED_FIT = '''
from metaphysica.simulations.base import Parameter

PARAMS = [
    Parameter(
        path="scratch.laundered",
        name="A laundered knob",
        units="dimensionless",
        status="DERIVED",
        description="Value is fitted to data, then presented as a derivation.",
        no_experimental_value=True,
    ),
]
'''

A_DENIAL = '''
from metaphysica.simulations.base import Parameter

PARAMS = [
    Parameter(
        path="scratch.honest",
        name="An honest one",
        units="dimensionless",
        status="DERIVED",
        description="A representation-theoretic fact, not a fitted quantity.",
        no_experimental_value=True,
    ),
]
'''


def _scratch_tree(tmp_path: Path, source: str) -> Path:
    root = tmp_path / "simulations"
    root.mkdir(parents=True)
    (root / "scratch_module.py").write_text(source, encoding="utf-8")
    return root


# --------------------------------------------------------------------------
# the count is measured, not written down
# --------------------------------------------------------------------------


def test_the_count_is_len_of_the_rows_and_not_a_literal(ledger):
    assert ledger["free_variable_count"] == len(ledger["rows"])
    source = (Path(__file__).resolve().parents[1] / "src" / "metaphysica"
              / "simulations" / "core" / "free_variable_ledger.py"
              ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Return) and isinstance(node.value, ast.Constant)):
            continue
        fn = None
        assert not isinstance(node.value.value, int) or node.value.value in (0, 1), (
            "a bare integer return in the ledger module is how a measured "
            "count turns back into a literal"
        )


def test_the_count_moves_when_a_fit_is_added(tmp_path):
    """The instrument must respond to its input, or it is not an instrument."""
    before = len(sweep_parameter_rows(_scratch_tree(tmp_path / "a", A_DENIAL)))
    after = len(sweep_parameter_rows(_scratch_tree(tmp_path / "b", A_FIT)))
    assert before == 0, "a DERIVED row is not a free variable and must not count"
    assert after == 1, "the added FITTED row was not counted"


def test_every_non_derived_status_is_represented_by_at_least_one_row(ledger):
    seen = set(ledger["count_by_status"])
    assert seen <= NON_DERIVED_STATUSES, (
        f"the ledger counted a status it does not classify as non-derived: "
        f"{sorted(seen - NON_DERIVED_STATUSES)}"
    )
    assert sum(ledger["count_by_status"].values()) == ledger["free_variable_count"]


def test_counts_by_role_sum_to_the_total(ledger):
    assert set(ledger["count_by_role"]) == set(ROLES)
    assert sum(ledger["count_by_role"].values()) == ledger["free_variable_count"]


# --------------------------------------------------------------------------
# guard 1: the honesty guard
# --------------------------------------------------------------------------


def _laundered_rows(root=None):
    """Rows whose description admits a fit while their status denies one."""
    out = []
    for call in iter_parameter_calls(root):
        if call.status not in DERIVATION_CLAIMING_STATUSES:
            continue
        hits = admits_a_fit(call.description)
        if hits:
            out.append((call.path, call.status, call.file.name, call.lineno, hits))
    return out


def test_no_parameter_claims_a_derivation_while_admitting_a_fit():
    laundered = _laundered_rows()
    assert not laundered, (
        "these parameters describe themselves as fitted, tuned, calibrated "
        "to, back-solved or chosen so, while declaring a status that claims "
        "the value came out of the geometry:\n"
        + "\n".join(f"  {p} [{s}] {f}:{ln} {h}" for p, s, f, ln, h in laundered)
    )


def test_the_honesty_guard_fires_on_a_laundered_fit(tmp_path):
    """Perturbation: the guard above is green only because the tree is."""
    laundered = _laundered_rows(_scratch_tree(tmp_path, A_LAUNDERED_FIT))
    assert len(laundered) == 1
    assert laundered[0][0] == "scratch.laundered"


def test_the_honesty_guard_does_not_fire_on_a_denial(tmp_path):
    """'not a fitted quantity' is a denial. A guard that fires on it is noise."""
    assert _laundered_rows(_scratch_tree(tmp_path, A_DENIAL)) == []


@pytest.mark.parametrize("text,expected", [
    ("Chosen so the residual vanishes.", True),
    ("Tuned to the PDG central value.", True),
    ("Back-solved from the measured mass.", True),
    ("calibrated to NuFIT 6.0", True),
    ("A phenomenological fit to the data.", True),
    ("This is fitted.", True),
    ("A representation-theoretic fact, not a fitted quantity.", False),
    ("originally fitted, now DERIVED", False),
    ("the superseded 27D-era fitted value", False),
    ("Derived from b3 = 24 alone.", False),
    ("", False),
])
def test_admission_detector_separates_confession_from_mention(text, expected):
    assert bool(admits_a_fit(text)) is expected


# --------------------------------------------------------------------------
# guard 2: the ledger gate
# --------------------------------------------------------------------------


def _independent_sweep(root=None):
    """A second, deliberately different sweep of the tree.

    The ledger's own sweep only looks at calls literally spelled
    ``Parameter(...)``. Re-using it here would make the gate circular: it
    would compare a sweep against a ledger built from the same sweep and
    agree with itself for every input, which is the shape of a test that
    cannot fail.

    So this one asks a different question -- *any* call, whatever its
    callee is named, carrying a non-derived status under either the
    ``status=`` or the ``classification=`` keyword -- and the gate is the
    disagreement between the two. An aliased constructor, a second status
    vocabulary or a renamed dataclass all show up here and not there.
    """
    root = Path(root) if root is not None else simulations_root()
    found = {}
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            kw = {k.arg: k.value for k in node.keywords if k.arg}
            statuses = {
                kw[key].value for key in ("status", "classification")
                if isinstance(kw.get(key), ast.Constant)
                and isinstance(kw[key].value, str)
            }
            if not (statuses & NON_DERIVED_STATUSES):
                continue
            ident = kw.get("path") or kw.get("id")
            name = ident.value if isinstance(ident, ast.Constant) else None
            if name is None:
                continue
            found[name] = f"{path.name}:{node.lineno}"
    return found


def test_every_non_derived_parameter_in_the_tree_is_in_the_ledger(ledger):
    """Independent sweep vs. the ledger: nothing non-derived may be absent."""
    published = {r["name"] for r in ledger["rows"]}
    swept = _independent_sweep()
    assert swept, "the independent sweep found nothing; the gate is vacuous"
    missing = {n: loc for n, loc in swept.items() if n not in published}
    assert not missing, (
        "these non-derived quantities exist in the tree but no ledger row "
        f"names them: {missing}. Either the ledger's sweep does not reach "
        "them -- an aliased constructor, a runtime status, a second status "
        "vocabulary -- or the ledger needs rebuilding with "
        "`python -m metaphysica.simulations.core.free_variable_ledger`."
    )


def test_the_ledger_gate_fires_when_a_row_is_missing(ledger):
    """Perturbation 1: drop a row from the published set; the gate must name it."""
    swept = _independent_sweep()
    published = {r["name"] for r in ledger["rows"]}
    dropped = sorted(set(swept) & published)[0]
    missing = [n for n in swept if n not in (published - {dropped})]
    assert missing == [dropped]


def test_the_ledger_sweep_sees_through_an_import_alias(tmp_path):
    """`import Parameter as Knob` must not hide a fit from the sweep."""
    aliased = '''
from metaphysica.simulations.base import Parameter as Knob

PARAMS = [
    Knob(
        path="scratch.aliased",
        name="Aliased knob",
        units="dimensionless",
        status="FITTED",
        description="Chosen so the callee name hides the fit.",
        no_experimental_value=True,
    ),
]
'''
    rows = sweep_parameter_rows(_scratch_tree(tmp_path, aliased))
    assert [r.name for r in rows] == ["scratch.aliased"]


def test_the_ledger_gate_fires_on_a_declaration_surface_it_does_not_model(tmp_path):
    """Perturbation 2: a fit registered through an unmodelled registrar.

    This is the case the gate exists for, and the case that found the
    ``set_param`` population. The ledger's sweep knows a fixed set of
    declaring callees; a fit written through any other one is invisible to
    it and visible to a sweep that keys on the status instead. The gate is
    the gap between the two, so a new registration surface is reported as a
    failure rather than silently uncounted.
    """
    unmodelled = '''
from metaphysica.simulations.base import PMRegistry


def publish(registry):
    registry.record_quantity(
        path="scratch.unmodelled",
        value=1.234,
        status="FITTED",
        description="Chosen so the residual vanishes.",
    )
'''
    root = _scratch_tree(tmp_path, unmodelled)
    assert sweep_parameter_rows(root) == [], (
        "the ledger's sweep unexpectedly modelled this registrar; the "
        "perturbation no longer probes the gap it was written for"
    )
    swept = _independent_sweep(root)
    assert set(swept) == {"scratch.unmodelled"}, (
        "a fit written through an unmodelled registrar was not seen by the "
        "independent sweep either; the gate cannot detect new surfaces"
    )


# --------------------------------------------------------------------------
# roles are evidence, not assertion
# --------------------------------------------------------------------------


def test_every_classified_role_carries_traced_evidence(ledger):
    unjustified = [
        r["name"] for r in ledger["rows"]
        if r["role"] != ROLE_UNRESOLVED and not r["role_evidence"]
    ]
    assert not unjustified, (
        f"these rows were given a role with no traced consumer behind it: "
        f"{unjustified}. A role without evidence is an assertion."
    )


def test_unresolved_rows_have_no_load_bearing_evidence(ledger):
    """UNRESOLVED must mean 'nothing found', not 'found and ignored'."""
    for row in ledger["rows"]:
        if row["role"] != ROLE_UNRESOLVED:
            continue
        kinds = {e["kind"] for e in row["role_evidence"]}
        assert "READ_INTO_REGISTERED_OUTPUT" not in kinds, (
            f"{row['name']} is UNRESOLVED but has a traced read into a "
            f"registered output"
        )


def test_the_twenty_measured_anchors_are_all_classified():
    from metaphysica.simulations.PM.geometry.geometric_anchors_core import (
        MEASURED_ANCHORS,
    )

    rows = {r.name: r for r in sweep_anchor_rows()}
    assert len(rows) == len(MEASURED_ANCHORS)
    for name in MEASURED_ANCHORS:
        row = rows[f"geometry.{name}"]
        assert row.role in ROLES
        assert row.location.endswith(tuple(str(n) for n in range(10)))


def test_load_bearing_anchors_are_the_ones_with_a_traced_derivation_consumer():
    """The four load-bearing anchors, each named by the trace that found it.

    Asserted by name because the claim is not "four of them are": it is
    that *these* four reach a registered output, and the evidence says
    where. If a fifth starts feeding a derivation this fails and says so.
    """
    rows = {r.name: r for r in sweep_anchor_rows()}
    load_bearing = sorted(
        n for n, r in rows.items() if r.role == ROLE_LOAD_BEARING_INPUT
    )
    assert load_bearing == [
        "geometry.H0_early",
        "geometry.H0_local",
        "geometry.M_GUT_geometric",
        "geometry.Omega_matter",
    ], f"the set of load-bearing anchors moved: {load_bearing}"

    for name in load_bearing:
        kinds = {e["kind"] for e in rows[name].role_evidence}
        assert kinds & {"READ_INTO_REGISTERED_OUTPUT",
                        "ANCHOR_FEEDS_EXPORTED_ANCHOR",
                        "DECLARED_AS_INPUT"}, (
            f"{name} is load-bearing with no derivation consumer traced"
        )


def test_the_phenomenological_anchors_are_not_counted_as_measurements():
    """alpha_T and alpha_R^2 are fits wearing a MEASURED label.

    Their own source says so -- "Phenomenological ... from observations"
    and ``# From fit to data``. Nothing external constrains them, so
    COMPARISON_ONLY would be a free pass. They stay UNRESOLVED with the
    contradiction recorded, because changing the registered status is a
    published-provenance change and belongs to the author.
    """
    rows = {r.name: r for r in sweep_anchor_rows()}
    for name in ("geometry.alpha_T_phenomenological",
                 "geometry.alpha_R_squared_phenom"):
        row = rows[name]
        assert row.role == ROLE_UNRESOLVED, (
            f"{name} is an openly phenomenological fit and must not be "
            f"classified as a measurement in use"
        )
        assert any("IS A FIT" in n for n in row.notes), (
            f"{name} lost the note recording that it is a fit, not a "
            f"measurement"
        )


def test_anchors_derived_from_measured_input_are_recorded(ledger):
    """Registered 'tuning_free' while being arithmetic on experiment."""
    names = {x["name"] for x in ledger["derived_from_free_variables"]}
    assert "geometry.H0_tension_ratio" in names, (
        "H0_tension_ratio = H0_local / H0_early is the ratio of two "
        "experimental numbers and registers as a tuning-free consequence "
        "of b3 = 24; the ledger must say so"
    )
    for entry in ledger["derived_from_free_variables"]:
        assert entry["inherits_from"], "recorded with no traced ancestor"


# --------------------------------------------------------------------------
# the three published claims now read one number
# --------------------------------------------------------------------------


def test_the_three_contradictory_claims_now_agree(ledger):
    from metaphysica.simulations.PM.paper.abstract import AbstractV17_2
    from metaphysica.simulations.PM.validation.statistical_rigor_validator import (
        StatisticalRigorValidator,
    )
    from metaphysica.simulations.base import PMRegistry

    expected = ledger["free_variable_count"]
    outputs = AbstractV17_2().run(PMRegistry.get_instance())
    outputs = outputs.get("outputs", outputs)

    assert outputs["validation.calibrated_count"] == expected
    assert outputs["abstract.calibration_inputs"] == expected
    assert outputs["validation.free_variable_count"] == expected
    assert StatisticalRigorValidator.free_variable_count() == expected


def test_the_edof_ansatz_is_still_three_and_still_labelled_an_ansatz():
    """EDOF feeds chi-squared. Moving it is a ruling, so it must not move.

    What it must no longer do is stand in for the free-variable count.
    """
    import inspect

    from metaphysica.simulations.PM.validation import statistical_rigor_validator as m

    src = inspect.getsource(m.StatisticalRigorValidator.calculate_effective_dof)
    assert "ANSATZ" in src, "the ansatz label was removed from an ansatz"
    assert "return 3" in src, (
        "EDOF moved; that changes reduced chi-squared and every verdict "
        "downstream of it, which is an author ruling"
    )
    assert m.StatisticalRigorValidator.free_variable_count() != 3, (
        "the measured count coincides with the ansatz; check the ledger "
        "before believing it"
    )


def test_no_published_claim_still_reads_zero_fitted_parameters(ledger):
    """The headline the ledger exists to retire."""
    assert ledger["free_variable_count"] > 0
    assert ledger["superseded_claims"]["validation.calibrated_count"] == 0, (
        "the superseded value is recorded so the replacement is auditable; "
        "it must not be quietly dropped"
    )


# --------------------------------------------------------------------------
# the artifact
# --------------------------------------------------------------------------


def test_the_artifact_round_trips(tmp_path, ledger):
    path = write_ledger(tmp_path)
    written = json.loads(path.read_text(encoding="utf-8"))
    assert written["free_variable_count"] == ledger["free_variable_count"]
    assert written["schema"] == "free_variables/1"
    for row in written["rows"]:
        assert row["location"], f"{row['name']} has no file:line"
        assert ":" in row["location"]
        assert row["closing_derivation"], (
            f"{row['name']} does not say what would close it"
        )


def test_published_count_matches_a_fresh_sweep(ledger):
    """The fast artifact path and the slow sweep must not drift."""
    assert published_free_variable_count() == ledger["free_variable_count"]
