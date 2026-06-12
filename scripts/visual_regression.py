"""Visual regression suite for the metaphysica static site.

Captures full-page screenshots of every ``Pages/*.html`` after a fresh build
and diffs them against a stored baseline. Useful for catching CSS / layout
regressions during paper polish work.

Two CLI modes:

* ``capture`` — launch a local HTTP server, load each page in Chromium,
  wait for the ``pm-content-ready`` event (or 2s timeout), then write
  ``<out>/<page_name>.png``.
* ``diff`` — compare a candidate screenshot set against a baseline set
  using a pixel-by-pixel Pillow diff. Emits ``diff_<page_name>.png`` with
  red highlighting and prints a one-line-per-page summary.

Dependencies (install on demand, not at module-import time so ``--help``
works in minimal envs):

    pip install playwright pillow
    playwright install chromium

Usage::

    python scripts/visual_regression.py capture \\
        --root src/metaphysica/website --out tests/visual_baselines
    python scripts/visual_regression.py diff \\
        --baseline tests/visual_baselines --candidate /tmp/visual_candidate

Reference: ``TIER_2_3_ROADMAP.md §T4.5`` (Sprint T2 task #7).
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Tuple

DEFAULT_READY_EVENT = "pm-content-ready"
DEFAULT_READY_TIMEOUT_MS = 2000
DEFAULT_VIEWPORT = (1280, 800)
DEFAULT_PORT = 8765
DIFF_THRESHOLD_PCT = 0.0  # ``diff`` reports raw pct; CI gates separately.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _iter_pages(root: Path) -> Iterator[Path]:
    """Yield every ``Pages/*.html`` under ``root``, sorted for stability."""
    pages_dir = root / "Pages"
    if not pages_dir.is_dir():
        raise FileNotFoundError(
            f"No Pages/ directory under {root}. Pass --root pointing at the "
            f"site root (typically src/metaphysica/website)."
        )
    yield from sorted(pages_dir.glob("*.html"))


@contextmanager
def _local_server(root: Path, port: int) -> Iterator[str]:
    """Start ``metaphysica.website.serve`` in a background thread.

    Yields the base URL (``http://localhost:<port>``). The server is stopped
    on context exit. We reuse the production serve module so headers,
    no-cache behaviour, and routing match the deployed site.
    """
    # Imported lazily so ``--help`` works without metaphysica installed.
    from metaphysica.website import serve as serve_mod

    httpd_holder: dict = {}

    def _run() -> None:
        import http.server
        import socketserver
        import os

        os.chdir(root)
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", port), serve_mod.CORSRequestHandler) as httpd:
            httpd_holder["server"] = httpd
            httpd.serve_forever()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    # Wait briefly for the server to bind.
    for _ in range(50):
        if "server" in httpd_holder:
            break
        time.sleep(0.02)
    else:
        raise RuntimeError(f"Local server failed to start on port {port}.")

    try:
        yield f"http://localhost:{port}"
    finally:
        server = httpd_holder.get("server")
        if server is not None:
            server.shutdown()
            server.server_close()
        thread.join(timeout=2)


# ---------------------------------------------------------------------------
# Capture mode
# ---------------------------------------------------------------------------

def capture(root: Path, out_dir: Path, port: int = DEFAULT_PORT) -> List[Path]:
    """Screenshot every ``Pages/*.html`` under ``root`` into ``out_dir``.

    Returns the list of written PNG paths.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError as exc:  # pragma: no cover — gated on optional dep
        raise SystemExit(
            "playwright is required for capture mode. "
            "Install with: pip install playwright && playwright install chromium"
        ) from exc

    pages = list(_iter_pages(root))
    if not pages:
        raise SystemExit(f"No Pages/*.html found under {root}.")

    out_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []

    with _local_server(root, port) as base_url, sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            context = browser.new_context(
                viewport={"width": DEFAULT_VIEWPORT[0], "height": DEFAULT_VIEWPORT[1]}
            )
            page = context.new_page()
            failures: List[str] = []
            for html in pages:
                target = f"{base_url}/Pages/{html.name}"
                print(f"  capture: {html.name}")
                page.goto(target, wait_until="domcontentloaded")
                try:
                    page.wait_for_event(
                        DEFAULT_READY_EVENT, timeout=DEFAULT_READY_TIMEOUT_MS
                    )
                except Exception:
                    # No event fired in time — fall back to a short wait so
                    # async content (MathJax, charts) gets a chance to render.
                    page.wait_for_timeout(DEFAULT_READY_TIMEOUT_MS)
                out_path = out_dir / f"{html.stem}.png"
                # Try full-page first; if the page is too tall for Chromium's
                # 16384px screenshot limit, fall back to viewport-only capture
                # so the run completes and produces a baseline for every page.
                try:
                    page.screenshot(path=str(out_path), full_page=True)
                except Exception as exc:  # noqa: BLE001 — log + degrade
                    print(f"    full-page failed ({exc.__class__.__name__}); "
                          f"retrying viewport-only")
                    try:
                        page.screenshot(path=str(out_path), full_page=False)
                    except Exception as exc2:  # noqa: BLE001
                        print(f"    viewport screenshot also failed: {exc2}")
                        failures.append(html.name)
                        continue
                written.append(out_path)
            if failures:
                print(f"  WARN: {len(failures)} page(s) failed: {failures}")
        finally:
            browser.close()

    print(f"\n  Captured {len(written)} screenshots to {out_dir}")
    return written


# ---------------------------------------------------------------------------
# Diff mode
# ---------------------------------------------------------------------------

def _diff_pair(baseline_png: Path, candidate_png: Path, out_png: Path) -> float:
    """Compare two PNGs pixel-by-pixel. Writes a diff overlay to ``out_png``
    where mismatched pixels are painted red. Returns the % of differing
    pixels (0.0 — 100.0).
    """
    from PIL import Image, ImageChops  # type: ignore

    base = Image.open(baseline_png).convert("RGB")
    cand = Image.open(candidate_png).convert("RGB")

    # Resize candidate to baseline dims if they drifted (e.g. different
    # viewport). Resizing rather than failing keeps the diff actionable.
    if base.size != cand.size:
        cand = cand.resize(base.size)

    diff = ImageChops.difference(base, cand)
    bbox = diff.getbbox()
    if bbox is None:
        # No difference. Still write an all-zero overlay so consumers can
        # always find a diff_*.png next to the candidate.
        Image.new("RGB", base.size, (0, 0, 0)).save(out_png)
        return 0.0

    # Build a red-overlay diff image.
    mask = diff.convert("L").point(lambda px: 255 if px > 0 else 0)
    overlay = base.copy()
    red = Image.new("RGB", base.size, (255, 0, 0))
    overlay.paste(red, mask=mask)
    overlay.save(out_png)

    total = base.size[0] * base.size[1]
    differing = sum(1 for px in mask.getdata() if px > 0)
    return 100.0 * differing / total


def diff(baseline_dir: Path, candidate_dir: Path) -> List[Tuple[str, float]]:
    """Diff every PNG in ``candidate_dir`` against ``baseline_dir``.

    Returns a list of ``(page_name, pct_different)`` tuples. Pages present
    in the candidate but missing from the baseline are reported with
    ``pct = float("inf")``.
    """
    try:
        import PIL  # noqa: F401
    except ImportError as exc:  # pragma: no cover — gated on optional dep
        raise SystemExit("Pillow is required for diff mode. Install with: pip install pillow") from exc

    if not baseline_dir.is_dir():
        raise SystemExit(f"Baseline directory not found: {baseline_dir}")
    if not candidate_dir.is_dir():
        raise SystemExit(f"Candidate directory not found: {candidate_dir}")

    results: List[Tuple[str, float]] = []
    for candidate_png in sorted(candidate_dir.glob("*.png")):
        if candidate_png.name.startswith("diff_"):
            continue
        baseline_png = baseline_dir / candidate_png.name
        if not baseline_png.is_file():
            print(f"  {candidate_png.name}: MISSING from baseline")
            results.append((candidate_png.stem, float("inf")))
            continue
        out_png = candidate_dir / f"diff_{candidate_png.name}"
        pct = _diff_pair(baseline_png, candidate_png, out_png)
        marker = "OK" if pct <= DIFF_THRESHOLD_PCT else "DIFF"
        print(f"  {candidate_png.stem:40s} {pct:6.3f}%  [{marker}]")
        results.append((candidate_png.stem, pct))

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="visual_regression",
        description=(
            "Capture screenshots of Pages/*.html and diff against a baseline. "
            "Sprint T2 task #7 / TIER_2_3_ROADMAP §T4.5."
        ),
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    cap = sub.add_parser("capture", help="Screenshot every Pages/*.html.")
    cap.add_argument(
        "--root", type=Path, required=True,
        help="Site root containing Pages/ (e.g. src/metaphysica/website).",
    )
    cap.add_argument(
        "--out", type=Path, required=True,
        help="Directory to write *.png screenshots into.",
    )
    cap.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Local HTTP server port (default: {DEFAULT_PORT}).",
    )

    df = sub.add_parser("diff", help="Diff candidate screenshots vs baseline.")
    df.add_argument("--baseline", type=Path, required=True, help="Baseline PNG dir.")
    df.add_argument("--candidate", type=Path, required=True, help="Candidate PNG dir.")
    df.add_argument(
        "--fail-threshold", type=float, default=0.1,
        help="Exit non-zero if any page diff exceeds this pct (default 0.1).",
    )
    return df.parent if False else parser  # keep ``parser`` reachable


def main(argv: List[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.mode == "capture":
        capture(args.root.resolve(), args.out.resolve(), port=args.port)
        return 0

    if args.mode == "diff":
        results = diff(args.baseline.resolve(), args.candidate.resolve())
        worst = max((pct for _, pct in results), default=0.0)
        print(f"\n  Worst diff: {worst:.3f}%  (threshold: {args.fail_threshold}%)")
        return 0 if worst <= args.fail_threshold else 1

    parser.error(f"Unknown mode: {args.mode}")
    return 2  # unreachable


if __name__ == "__main__":
    sys.exit(main())
