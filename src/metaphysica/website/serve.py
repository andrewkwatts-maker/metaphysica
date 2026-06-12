"""Local HTTP server for the bundled PrincipiaMetaphysica static site.

Exposes the ``metaphysica-serve`` console-script entry point. The server is a
thin :class:`http.server.SimpleHTTPRequestHandler` subclass that adds
permissive CORS headers and disables caching so that local development
matches the deployed static-site behaviour.

The implementation deliberately avoids any third-party dependency so this can
be invoked immediately after ``pip install metaphysica`` without pulling the
``[full]`` extras.

Usage::

    metaphysica-serve                       # serve current directory on :8000
    metaphysica-serve --root build/site     # serve a built site
    metaphysica-serve --port 8080 --no-browser

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import argparse
import http.server
import os
import socket
import socketserver
import sys
import webbrowser
from pathlib import Path
from typing import Sequence

DEFAULT_PORT = 8000
PORT_SCAN_RANGE = 100


class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler with CORS + no-cache headers."""

    def end_headers(self) -> None:  # noqa: D401 — short imperative is intentional
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802 — http.server naming convention
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        # Quiet 200s, surface anything else (4xx/5xx/etc.) so problems remain visible.
        joined = " ".join(str(a) for a in args)
        if "200" not in joined:
            print(f"  {args[0] if args else format}")


def _find_available_port(start_port: int, scan_range: int = PORT_SCAN_RANGE) -> int:
    """Return the first bindable port starting at ``start_port``.

    Falls back to ``start_port`` if nothing in the scan range is free (the
    subsequent bind attempt will then raise a clear error to the caller).
    """
    for port in range(start_port, start_port + scan_range):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("", port))
                return port
        except OSError:
            continue
    return start_port


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="metaphysica-serve",
        description=(
            "Serve a PrincipiaMetaphysica static site locally with CORS "
            "headers enabled and caching disabled."
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Directory to serve (default: current working directory).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"TCP port to listen on (default: {DEFAULT_PORT}). The next free "
        f"port in [PORT, PORT+{PORT_SCAN_RANGE}) is used if the requested one is busy.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the served site in the default web browser.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Console-script entry point. Returns a process exit code."""
    args = _parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"[metaphysica-serve] ERROR: --root {root} is not a directory.", file=sys.stderr)
        return 2

    os.chdir(root)

    port = _find_available_port(args.port)

    print("=" * 60)
    print("  PRINCIPIA METAPHYSICA - Local Server")
    print("=" * 60)
    print(f"\n  Starting server at http://localhost:{port}")
    print(f"  Serving files from: {root}")
    print("\n  Press Ctrl+C to stop the server\n")
    print("=" * 60)

    # ``allow_reuse_address`` keeps successive runs from hitting TIME_WAIT issues.
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
            if not args.no_browser:
                url = f"http://localhost:{port}/index.html"
                print(f"\n  Opening: {url}\n")
                try:
                    webbrowser.open(url)
                except Exception as exc:  # pragma: no cover — depends on env
                    print(f"  (Could not auto-open browser: {exc})")

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n\n  Server stopped.")
                return 0
    except OSError as exc:
        print(f"[metaphysica-serve] ERROR: could not bind port {port}: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
