"""XV-15: PM STOCHASTIC declares no subtree the rigor report no longer writes."""
from __future__ import annotations

import inspect

from metaphysica.simulations.PM.validation import statistical_rigor_validator as srv
from metaphysica.theories.pm import results


def test_stochastic_declares_no_removed_jacobian_key():
    for name, pointers in results.STOCHASTIC.items():
        assert "/jacobian_analysis" not in pointers, name
    assert not hasattr(srv.StatisticalRigorValidator, "generate_jacobian_matrix")


def test_stochastic_comment_does_not_describe_the_removed_stub():
    src = inspect.getsource(results)
    assert "JACOBIAN_STUB_SEED" not in src
    assert "still a STUB" not in src
