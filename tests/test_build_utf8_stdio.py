"""A build whose stdout is a cp1252 file must still print Unicode."""
from __future__ import annotations

import importlib
import io

build_mod = importlib.import_module("metaphysica.build")


def test_utf8_stdio_lets_a_cp1252_stream_print_unicode():
    raw = io.BytesIO()
    stream = io.TextIOWrapper(raw, encoding="cp1252")
    build_mod._utf8_stdio([stream])
    print("χ² → ok", file=stream)
    stream.flush()
    assert raw.getvalue().decode("utf-8").strip() == "χ² → ok"


def test_utf8_stdio_skips_streams_without_reconfigure():
    build_mod._utf8_stdio([io.StringIO()])
