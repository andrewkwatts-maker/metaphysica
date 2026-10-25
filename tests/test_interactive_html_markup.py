"""Hover markup for a formula must not be rewritten by a later symbol.

FOUND 2026-10-25: substituting each symbol's span straight into the html let
a shorter symbol match inside markup an earlier one inserted -- 'n' inside
'span' -- so four published formulas began '<spa<span' or 'd<span'. The
chi^2 formula of section 7 was one of them.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import re

from metaphysica.generators.generate_interactive_html import (
    generate_interactive_html,
)


def _formula():
    return {
        "plain_text": "chi^2 = 12.5 over n = 4 rows",
        "terms": {"chi^2": "Global chi-squared", "n": "Number of scoring rows",
                  "r": "a letter also inside every span tag"},
    }


def test_no_symbol_is_substituted_inside_inserted_markup():
    html = generate_interactive_html(_formula())
    assert html.startswith("<span class=\"formula-var\" data-term=\"chi^2\">")
    tags = re.findall(r"<[^>]*>", html)
    assert all(t in ("</span>",) or t.startswith("<span class=") for t in tags)
    assert "<spa<" not in html and "d<span" not in html


def test_every_symbol_gets_exactly_one_hover():
    html = generate_interactive_html(_formula())
    for sym in ("chi^2", "n", "r"):
        assert html.count('data-term="%s"' % sym) == 1
