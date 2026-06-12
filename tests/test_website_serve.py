"""Smoke tests for :mod:`metaphysica.website.serve`.

These tests verify that the ``metaphysica-serve`` console-script entry point
imports cleanly and parses arguments without raising. We deliberately do NOT
start the HTTP server in tests — that would bind a real socket, which is
brittle in CI sandboxes and outside the scope of "entry point exists".
"""

from __future__ import annotations

import argparse

import pytest


def test_main_importable() -> None:
    """``main`` must be importable as the console-script entry point."""
    from metaphysica.website.serve import main

    assert callable(main)


def test_cors_handler_importable() -> None:
    """The handler class is exported for downstream extension."""
    import http.server

    from metaphysica.website.serve import CORSRequestHandler

    assert issubclass(CORSRequestHandler, http.server.SimpleHTTPRequestHandler)


def test_parse_args_defaults() -> None:
    """Argument parser builds without raising on an empty argv."""
    from metaphysica.website import serve

    ns = serve._parse_args([])
    assert isinstance(ns, argparse.Namespace)
    assert ns.port == serve.DEFAULT_PORT
    assert ns.no_browser is False
    # --root defaults to "." (resolved later in main())
    assert str(ns.root) == "."


def test_parse_args_custom() -> None:
    """Explicit flags are picked up correctly."""
    from metaphysica.website import serve

    ns = serve._parse_args(["--port", "9001", "--no-browser", "--root", "site"])
    assert ns.port == 9001
    assert ns.no_browser is True
    assert str(ns.root) == "site"


def test_main_rejects_missing_root(tmp_path) -> None:
    """``main`` should refuse a --root that does not exist (exit code 2)."""
    from metaphysica.website.serve import main

    missing = tmp_path / "does-not-exist"
    rc = main(["--root", str(missing), "--no-browser", "--port", "0"])
    assert rc == 2


def test_find_available_port_returns_int() -> None:
    """Port scan returns a usable integer in the requested range."""
    from metaphysica.website.serve import _find_available_port

    port = _find_available_port(54000, scan_range=5)
    assert isinstance(port, int)
    assert port >= 54000


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
