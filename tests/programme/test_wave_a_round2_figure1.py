"""Wave A round 2, R2-18 (and the figure part of R2-16): figure 1 draws the bulk of the path
in force, read from the ``bulk_signature`` fork: its dimension, its signature and every time.
No three-sector 27D decomposition, no single time fibre, no "M27" in the printed text.

The labels are read from the label builders; nothing is rendered.
"""
import inspect

import pytest

from metaphysica.simulations.core import variants
from metaphysica.simulations.visualizations import figure1_m27_decomposition as f1

B3 = 43  # any integer: the b3 label follows the registry row (close-out test of XA-09)
OPTIONS = variants.FORKS[f1.BULK_FORK].option_ids()
WITHDRAWN = ("T^1", "Time Fiber", "1D Timelike", "Unified Clock", "EIS", "Sampler", "27")


def _texts(option):
    with variants.forced({f1.BULK_FORK: option}):
        space, times = f1.bulk_from_path()
    return [label.text for label in f1.figure1_labels(B3, space, times)]


@pytest.mark.parametrize("option", OPTIONS)
def test_bulk_is_read_from_the_selected_option(option):
    """The parsed (space, times) is the signature the catalogue states for that option."""
    with variants.forced({f1.BULK_FORK: option}):
        space, times = f1.bulk_from_path()
    summary = next(o.summary for o in variants.FORKS[f1.BULK_FORK].options if o.id == option)
    assert f"{space + times}D at ({space},{times})" in summary


def test_path_in_force_is_the_adopted_bulk():
    """With nothing forced the figure draws what the fork resolves to."""
    space, times = f1.bulk_from_path()
    assert f"{space}_{times}" == variants.resolve(f1.BULK_FORK)


def test_adopted_path_draws_24_space_plus_2_times():
    # Labels of the adopted bulk: 26D (24,2), two 13D (12,1) shadows, one time each
    # (docs/claude-context.md "Facts that must not drift", read 2026-11-11).
    texts = _texts("24_2")
    for expected in (
        "$M^{26}(24,2)$ Bulk Decomposition",
        r"24 spatial $\oplus$ 2 timelike = 26 dimensions",
        "$M^{26}(24,2)$ - 26D Spacetime",
        "24 Spatial Dimensions",
        "Signature $(24,0)$",
        "2 Timelike Dimensions",
        "Signature $(0,2)$",
        "One Time per Shadow",
        r"2 $\times$ 13D$(12,1)$ Shadows",
        "Metric, signature $(24,2)$:",
        r"$ds^2 = - dt_1^2 - dt_2^2 + \sum_{i=1}^{24} dy_i^2$",
    ):
        assert expected in texts, expected


@pytest.mark.parametrize("option", OPTIONS)
def test_no_three_sector_decomposition_and_no_single_time_fibre(option):
    texts = _texts(option)
    for stale in WITHDRAWN:
        assert not any(stale in text for text in texts), stale


@pytest.mark.parametrize("option", OPTIONS)
def test_boxes_add_up_to_the_bulk_dimension(option):
    """The spatial box and the timelike box are the whole bulk: nothing is left for a third."""
    with variants.forced({f1.BULK_FORK: option}):
        space, times = f1.bulk_from_path()
    heads = [f1.space_labels(space, B3)[0].text, f1.time_labels(space, times)[0].text]
    assert [int(head.split()[0]) for head in heads] == [space, times]
    assert f"= {space + times} dimensions" in f1.title_labels(space, times)[1].text


@pytest.mark.parametrize("option", OPTIONS)
def test_metric_has_one_minus_sign_per_time(option):
    with variants.forced({f1.BULK_FORK: option}):
        space, times = f1.bulk_from_path()
    metric = f1.metric_tex(space, times)
    assert metric.count("- dt_") == times
    assert f"^{{{space}}} dy_i^2" in metric


def test_forced_two_time_option_draws_its_own_bulk():
    # The 26_2 option's consequence text states "two 14D(13,1) shadows".
    texts = _texts("26_2")
    assert "$M^{28}(26,2)$ Bulk Decomposition" in texts
    assert r"2 $\times$ 14D$(13,1)$ Shadows" in texts
    assert "$14D$" in texts and "$13D$" not in texts
    assert not any("Leech" in text for text in texts)


def test_forced_one_time_option_has_no_shadow_split():
    texts = _texts("25_1")
    assert "$M^{26}(25,1)$ Bulk Decomposition" in texts
    assert "1 Timelike Dimension" in texts
    assert r"$ds^2 = - dt_1^2 + \sum_{i=1}^{25} dy_i^2$" in texts
    assert not any("Shadow" in text or "Bridge Pairs" in text for text in texts)
    assert [dim for dim, _ in f1.descent_chain(25, 1)] == ["$26D$", "$7D$", "$4D$"]


def test_option_of_another_shape_raises(monkeypatch):
    monkeypatch.setattr(f1, "resolve", lambda fork_id: "27")
    with pytest.raises(ValueError):
        f1.bulk_from_path()


def test_space_that_does_not_split_over_the_times_raises():
    with pytest.raises(ValueError):
        f1.shadow_signature(25, 2)


def test_printed_text_names_the_bulk_of_the_path():
    assert "M27" not in inspect.getsource(f1)
    assert "M^26(24,2)" in f1.status_line(24, 2)
    assert "M^28(26,2)" in f1.status_line(26, 2)


def test_no_function_of_the_module_is_oversize():
    """R2-16: generate_figure1_m27_decomposition had grown to 131 lines."""
    for name, func in inspect.getmembers(f1, inspect.isfunction):
        if func.__module__ == f1.__name__:
            assert len(inspect.getsource(func).splitlines()) <= 60, name
