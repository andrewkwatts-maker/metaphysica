"""Track G1/G3: selections as data and declared fork compatibility."""
import json
import pytest

from metaphysica.simulations.core import variants as v
from metaphysica.simulations.core import switch_search as ss

BAD = {"b3_seed": "seed_43_joyce", "n_gen_source": "b3_over_dim_O"}


def test_selection_id_active_when_no_departures():
    assert v.selection_id({}) == "active"
    assert v.selection_id({f: fk.default() for f, fk in v.FORKS.items()}) == "active"


def test_selection_id_ignores_defaults_and_key_order():
    a = {"b3_seed": "seed_24", "h0_route": "kk_bridge"}
    b = {"h0_route": "kk_bridge", "spectral_index_route": v.FORKS["spectral_index_route"].default(), "b3_seed": "seed_24"}
    assert v.selection_id(a) == v.selection_id(b) != "active"
    assert v.departures(b) == a


def test_load_selection_rejects_unknown_fork_and_option(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"no_such_fork": "x"}))
    with pytest.raises(ValueError, match="no_such_fork"):
        v.load_selection(p)
    p.write_text(json.dumps({"b3_seed": "nope"}))
    with pytest.raises(ValueError, match="nope"):
        v.load_selection(p)


def test_resolve_honours_selection_between_override_and_env(tmp_path, monkeypatch):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"h0_route": "kk_bridge"}))
    monkeypatch.setenv("METAPHYSICA_SELECTION", str(p))
    monkeypatch.setenv("METAPHYSICA_VARIANT_H0_ROUTE", "ricci_flow")
    assert v.resolve("h0_route") == "kk_bridge"
    assert v.resolve("h0_route", "ricci_flow") == "ricci_flow"
    assert v.resolve("b3_seed") == v.FORKS["b3_seed"].default()


def test_bad_selection_file_fails_in_resolve(tmp_path, monkeypatch):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"h0_route": "zzz"}))
    monkeypatch.setenv("METAPHYSICA_SELECTION", str(p))
    with pytest.raises(ValueError, match="zzz"):
        v.resolve("h0_route")


def test_constraints_naming_unknown_options_fail_at_validation():
    opt = v.VariantOption(id="a", summary="", consequence="", adopted=True,
                          excludes=(("ghost_fork", "x"),))
    fork = v.Fork(id="f", question="", source="", options=[opt], status="OPEN")
    with pytest.raises(ValueError, match="ghost_fork"):
        v.validate_constraints({"f": fork})


def test_declared_exclusion_makes_selection_incompatible():
    assert v.compatible(v.active_selection())
    assert not v.compatible({**v.active_selection(), **BAD})
    assert v.violations({**v.active_selection(), **BAD})


def test_enumeration_prunes_before_expanding_and_matches_count():
    ids = ["b3_seed", "n_gen_source"]
    combos = ss.combinations_for(ids)
    assert combos and all(v.compatible(c) for c in combos)
    assert BAD not in combos
    assert combos[0] == {f: v.FORKS[f].default() for f in ids}
    assert len(combos) == ss.count_compatible(ids)
    full = len(v.FORKS["b3_seed"].options) * len(v.FORKS["n_gen_source"].options)
    assert len(combos) < full


def test_selection_file_reaches_n_gen_report(tmp_path, monkeypatch):
    """b3_path used to see n_gen_source only through its env var, so a
    selection naming it was silently ignored."""
    from metaphysica.simulations.PM.geometry import b3_path
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"n_gen_source": "b3_over_dim_O"}))
    monkeypatch.setenv("METAPHYSICA_SELECTION", str(p))
    assert b3_path.n_gen_report()["declared_source"] == "b3_over_dim_O"


def test_flavour_b3_follows_selection_over_env(tmp_path, monkeypatch):
    """yukawa_derivation read its env var before resolve(), so the env var
    outranked a selection file (track_g.md finding)."""
    from metaphysica.simulations.PM.particle import yukawa_derivation as y
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"flavour_seed_coupling": "calibrated_24"}))
    monkeypatch.setenv("METAPHYSICA_SELECTION", str(p))
    monkeypatch.setenv("METAPHYSICA_VARIANT_FLAVOUR_SEED_COUPLING", "follow_seed")
    assert y.resolve_flavour_b3() == y.DEFAULT_B3


def test_forced_outranks_a_selection_file(tmp_path, monkeypatch):
    """In-process comparisons forced forks through env vars, which a
    selection file outranks, so they silently measured the file's option."""
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"h0_route": "kk_bridge"}))
    monkeypatch.setenv("METAPHYSICA_SELECTION", str(p))
    with v.forced({"h0_route": "ricci_flow"}):
        assert v.resolve("h0_route") == "ricci_flow"
        assert v.is_explicit("h0_route")
    assert v.resolve("h0_route") == "kk_bridge"


def test_describe_treats_a_selection_file_as_a_path_run(tmp_path, monkeypatch):
    """describe() only skipped the drift check for env-var runs; a selection
    run was drift-checked, which halted path builds on 2026-10-25."""
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"h0_route": "kk_bridge"}))
    monkeypatch.setenv("METAPHYSICA_SELECTION", str(p))
    entry = v.describe()["forks"]["h0_route"]
    assert entry["selected"] == "kk_bridge"
    if v.FORKS["h0_route"].read_adopted is not None:
        assert entry["source_read"].startswith("not_checked")


def test_no_module_forces_forks_by_hand():
    """One mechanism (variants.forced) instead of three env-var copies."""
    import pathlib
    core = pathlib.Path(v.__file__).parent.parent  # the package sits in core/
    for name in ("fork_implications.py", "preferred_path.py", "switch_search.py"):
        assert "os.environ[key] = " not in (core / name).read_text(encoding="utf-8"), name
