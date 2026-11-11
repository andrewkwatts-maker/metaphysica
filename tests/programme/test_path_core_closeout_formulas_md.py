"""XP-12: FORMULAS.md (core/sync_docs.py) quotes the path, not seed 24.

The named-constants Markdown used to type 163/239 + 23/24 = 1.6403 as a
validated parity, 576/8 and 576/4 for chi_eff, 72 + 72 = 144, sqrt(24) for
lambda_S as if it were b3, and 71.55 as the H0 target. Each is now read from
the registry or the fork readers, and the parity is labelled an IDENTITY.
"""
import pytest

from metaphysica.simulations.core.FormulasRegistry import FormulasRegistry
from metaphysica.simulations.core.sync_docs import DocumentationSynchronizer
from metaphysica.simulations.core.variants import selection
from metaphysica.simulations.PM.cosmology.late_time_routes import de_betti_n

SEED_24_TEXT = ("163}}{{239", "{163}{239}", "1.6403", "71.55", "576/",
                "(24 Elders)", "72 + 72", "(7*24)", "B3=24")


def _md(registry=None):
    sync = DocumentationSynchronizer(registry=registry or FormulasRegistry(),
                                     output_dir=".")
    return sync.generate_formulas_md()


def test_no_untyped_seed_24_arithmetic():
    md = _md()
    assert [t for t in SEED_24_TEXT if t in md] == []


def test_parity_is_the_registry_identity_text():
    reg = FormulasRegistry()
    md = _md(reg)
    assert reg._parity_text() in md
    assert "Parity Identity (IDENTITY" in md


def test_b3_quotes_follow_the_seed_of_the_path():
    reg = FormulasRegistry()
    b3 = reg.elder_kads
    md = _md(reg)
    assert f"manifold base b3 = {b3} of the path" in md
    assert f"(7 * {b3}) - 5 = {reg.odowd_bulk_derived}" in md
    assert f"1/{reg.qedem_chi_sum}" in md


@pytest.mark.parametrize("option", ["b2_4", "b3_live"])
def test_sigma_t_fraction_follows_the_dark_energy_fork(option):
    with selection.forced({"dark_energy_betti": option}):
        md = _md()
    n = de_betti_n(option)
    assert f"-sigma_T = -{n - 1}/{n}" in md
    assert f"Void Seal ({n - 1}/{n}, dark_energy_betti fork)" in md


def test_generator_functions_fit_the_size_rule():
    import inspect
    for name, member in inspect.getmembers(DocumentationSynchronizer,
                                           inspect.isfunction):
        lines = len(inspect.getsource(member).splitlines())
        assert lines <= 60, (name, lines)
