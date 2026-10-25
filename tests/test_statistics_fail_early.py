"""generate_statistics fails early, with a reason, when no sigma set exists.

FOUND 2026-10-25: a path whose simulations were blocked left no
parameters.json; generate_statistics then died on KeyError 'chi_squared',
hiding the real cause.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
import pytest

from metaphysica.generators import generate_statistics as gs


def test_empty_inputs_raise_a_clear_error(tmp_path, monkeypatch):
    for name in ("GATES_CERT_FILE", "PARAM_CERT_FILE", "STATISTICAL_RIGOR_FILE",
                 "PARAMETERS_FILE"):
        monkeypatch.setattr(gs, name, str(tmp_path / (name + ".json")))
    with pytest.raises(RuntimeError, match="earlier build step failed"):
        gs.generate_statistics()
