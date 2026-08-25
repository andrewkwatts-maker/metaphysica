"""Tests for the generated registry-path namespace.

The path set must come from the live artifact, and an unknown path must
fail at the reference with a suggestion -- the module is pointless if a
typo still fails late with a bare KeyError somewhere downstream.
"""
import pytest

from metaphysica.simulations.core.registry_paths import P, PATHS, validate


def test_path_set_is_generated_not_toy():
    """A hand-typed list would be small; the artifact has hundreds."""
    assert len(PATHS()) > 500


def test_known_canonical_paths_validate():
    for path in ("topology.elder_kads", "cosmology.s8_pm_predicted",
                 "geometry.sum_m_nu", "ckm.V_us"):
        assert validate(path) == path
        assert path in P


def test_attribute_access_spells_the_dot():
    assert P.topology__elder_kads == "topology.elder_kads"


def test_typo_fails_at_the_reference_with_suggestion():
    with pytest.raises(KeyError) as exc:
        validate("topology.elder_kad")  # missing trailing 's'
    assert "elder_kads" in str(exc.value), "suggestion must name the fix"


def test_unknown_namespace_fails():
    with pytest.raises(KeyError):
        _ = P.no_such__parameter_path
