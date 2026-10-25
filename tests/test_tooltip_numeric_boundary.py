"""A numeric tooltip term must not match inside a longer number
(bug: term '4' of b3-generations rendered '2<span>4</span>' inside '24/8')."""
from metaphysica.generators.generate_interactive_html import _replace_first_in_text

T = ""


def test_digit_term_skips_longer_number():
    assert _replace_first_in_text("N = 24/8 = 3", "4", T) is None


def test_digit_term_matches_standalone_number():
    assert _replace_first_in_text("N = b2/4 = 12/4 = 3", "4", T) == "N = b2/" + T + " = 12/4 = 3"


def test_digit_term_skips_decimal():
    assert _replace_first_in_text("x = 0.4 + 4", "4", T) == "x = 0.4 + " + T


def test_letter_terms_unchanged():
    assert _replace_first_in_text("ds^2 = -dt^2", "t", T) == "ds^2 = -d" + T + "^2"


def test_digit_term_after_range_dots():
    assert _replace_first_in_text("n=1..42 (all)", "42", T) == "n=1.." + T + " (all)"


def test_angle_brackets_in_plain_text_are_escaped():
    from metaphysica.generators.generate_interactive_html import generate_interactive_html
    html = generate_interactive_html({"plain_text": "<W(C)> = exp(-sigma * A)",
                                      "terms": {"sigma": "string tension", "<W(C)>": "Wilson loop"}})
    assert html.startswith('<span class="formula-var" data-term="&lt;W(C)&gt;">&lt;W(C)&gt;')
    assert "sigma<span" in html
