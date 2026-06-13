"""Sprint 6 — interactive ``metaphysica.help()`` plus the catalog CLI.

Two surfaces:

* :func:`help` — interactive pretty-printer that takes an entity name
  and prints a human-readable summary (kind, supported formats, key
  metadata, example ``get()`` call).
* :func:`cli` — the ``metaphysica`` console-script entry point with
  subcommands ``get`` / ``list`` / ``help`` / ``build``.

The CLI delegates to :func:`metaphysica.get` and :func:`metaphysica.build`
under the hood so behaviour stays in lock-step with the Python API.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, List, Optional

from ._catalog import (
    EntityRef,
    KIND_CONSTANT,
    KIND_FORMULA,
    KIND_GATE,
    KIND_PARAMETER,
    KIND_QUARK,
    KIND_SECTION,
    KINDS,
    resolve,
)
from ._errors import (
    MetaphysicaError,
    MetaphysicaFormatError,
    MetaphysicaKeyError,
)


# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------


def _summarise(ref: EntityRef) -> List[str]:
    """Return a list of "Key: value" lines summarising *ref* for humans."""
    p = ref.payload if isinstance(ref.payload, dict) else {}
    lines: List[str] = []
    title = (
        p.get("title")
        or p.get("label")
        or p.get("name")
        or p.get("Name")
        or ref.canonical_id
    )
    lines.append(f"  ID:      {ref.canonical_id}")
    if title and str(title) != ref.canonical_id:
        lines.append(f"  Title:   {title}")
    lines.append(f"  Kind:    {ref.kind}")
    lines.append(f"  Source:  {ref.source}")

    if ref.kind in (KIND_CONSTANT, KIND_PARAMETER, KIND_QUARK):
        value = p.get("value")
        if value is None:
            value = p.get("Mass_MeVc2")
        if value is not None:
            units = (
                (p.get("metadata") or {}).get("units")
                if isinstance(p.get("metadata"), dict)
                else None
            ) or p.get("units")
            lines.append(f"  Value:   {value}{' ' + units if units else ''}")
        desc = (
            ((p.get("metadata") or {}).get("description")
             if isinstance(p.get("metadata"), dict) else None)
            or p.get("description")
            or ""
        )
        if desc:
            lines.append(f"  Desc:    {_truncate(desc, 200)}")

    if ref.kind == KIND_FORMULA:
        latex = p.get("latex") or p.get("eml_latex")
        if latex:
            lines.append(f"  LaTeX:   {_truncate(latex, 120)}")
        if p.get("value") is not None:
            lines.append(f"  Value:   {p['value']}")
        if p.get("triple_status"):
            lines.append(f"  Triple:  {p['triple_status']}")

    if ref.kind == KIND_GATE:
        for k in ("status", "verdict", "block", "category"):
            v = p.get(k)
            if v is not None:
                lines.append(f"  {k.capitalize():8s} {v}")

    return lines


def _truncate(text: str, limit: int) -> str:
    """Shorten *text* to *limit* characters with a single-line ellipsis."""
    s = " ".join(str(text).split())
    return s if len(s) <= limit else s[: limit - 1] + "…"


def help(name: Optional[str] = None, *, kind: Optional[str] = None) -> None:
    """Pretty-print everything we know about *name* to stdout.

    With no argument, prints a high-level summary of the public API:
    available formats, kinds, counts per kind.
    """
    from ._get import _KIND_FORMATS, get_supported_formats

    if name is None:
        _print_overview()
        return

    try:
        ref = resolve(name, kind=kind)
    except MetaphysicaKeyError as exc:
        print(f"metaphysica.help: {exc}", file=sys.stderr)
        return

    print(f"metaphysica.help({name!r})")
    print()
    for line in _summarise(ref):
        print(line)

    print()
    formats = sorted(_KIND_FORMATS.get(ref.kind, set()))
    print(f"  Supported formats for kind={ref.kind!r}:")
    print(f"    {', '.join(formats)}")
    print()
    print("  Examples:")
    print(f"    metaphysica.get({ref.canonical_id!r}, fmt='json')")
    print(f"    metaphysica.GetLaTeX({ref.canonical_id!r})")
    if "png" in formats:
        print(
            f"    metaphysica.GetPNG({ref.canonical_id!r}, out_path='./{ref.canonical_id}.png')"
        )
    if "md" in formats:
        print(f"    metaphysica.GetMarkdown({ref.canonical_id!r})")


def _print_overview() -> None:
    """Print the high-level API summary that ``metaphysica.help()`` shows."""
    from ._catalog import list_kind as _list
    from ._get import _KIND_FORMATS, SUPPORTED_FORMATS

    print("metaphysica — unified physics framework lookup API")
    print()
    print("Entry points:")
    print("  metaphysica.build(out_dir=...)             — full pipeline (sims + site + PDF)")
    print("  metaphysica.run_all(out_dir=...)           — simulations only")
    print("  metaphysica.get(name, fmt=...)             — unified Get* dispatcher")
    print("  metaphysica.help('<name>')                 — what you're reading")
    print()
    print("Formats (Sprint 1-4):")
    print(f"  {', '.join(SUPPORTED_FORMATS)}")
    print()
    print("Typed aliases:")
    print("  GetJSON, GetYAML, GetLaTeX,")
    print("  GetArithma, GetEML, GetFloat,")
    print("  GetSVG, GetPNG,")
    print("  GetPDF, GetHTML, GetMarkdown")
    print()
    print("Kinds (with current catalog counts):")
    for kind in KINDS:
        try:
            n = len(_list(kind))
        except Exception:
            n = "?"
        print(f"  {kind:13s} {n}")
    print()
    print("Tip: pass a name to drill in, e.g. ``metaphysica.help('b3')``.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cli_get(args: argparse.Namespace) -> int:
    """Implement ``metaphysica get <name> --fmt <fmt> [--out path]``."""
    from . import get

    try:
        result = get(args.name, fmt=args.fmt, kind=args.kind, out_path=args.out)
    except MetaphysicaError as exc:
        print(f"metaphysica get: {exc}", file=sys.stderr)
        return 1

    if args.out:
        # Write-through already happened inside get(); echo a confirmation.
        print(f"Wrote {args.fmt} render of {args.name!r} → {args.out}")
        return 0

    # Print to stdout. Binary formats are base64-shielded so terminal
    # output stays sane.
    if isinstance(result, (bytes, bytearray)):
        import base64
        sys.stdout.write(base64.b64encode(bytes(result)).decode("ascii"))
        sys.stdout.write("\n")
    elif isinstance(result, dict):
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(str(result))
        if not str(result).endswith("\n"):
            sys.stdout.write("\n")
    return 0


def _cli_list(args: argparse.Namespace) -> int:
    """Implement ``metaphysica list [<kind>]``."""
    from ._catalog import list_kind
    from ._listing import list_all

    if args.kind:
        entries = list_kind(args.kind)
        for e in entries:
            print(e)
    else:
        for kind, entries in list_all().items():
            print(f"# {kind} ({len(entries)})")
            for e in entries:
                print(e)
            print()
    return 0


def _cli_help(args: argparse.Namespace) -> int:
    help(args.name, kind=args.kind)
    return 0


def _cli_build(args: argparse.Namespace) -> int:
    """Forward to :func:`metaphysica.build`."""
    from . import build

    return build(
        out_dir=args.out,
        fast=args.fast,
        skip_sims=args.skip_sims,
        only=args.only,
    )


def cli(argv: Optional[List[str]] = None) -> int:
    """``metaphysica`` console-script entry point.

    Subcommands:
      * ``get <name> [--fmt FMT] [--kind KIND] [--out PATH]``
      * ``list [<kind>]``
      * ``help [<name>] [--kind KIND]``
      * ``build [--out DIR] [--fast] [--skip-sims] [--only STEP]``
    """
    parser = argparse.ArgumentParser(
        prog="metaphysica",
        description="Unified API for the metaphysica physics framework.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("get", help="Retrieve an entity in any format.")
    g.add_argument("name", help="Entity name (constant / formula / gate / ...).")
    g.add_argument("--fmt", default="json",
                   help="Output format (json/yaml/latex/arithma/eml/float/svg/png/pdf/html/md).")
    g.add_argument("--kind", default=None,
                   help="Disambiguate by kind (constant / formula / ...).")
    g.add_argument("--out", default=None,
                   help="Write to this path instead of stdout.")
    g.set_defaults(func=_cli_get)

    ls = sub.add_parser("list", help="List entities (optionally per kind).")
    ls.add_argument("kind", nargs="?", default=None,
                    help="Kind to list (defaults to all).")
    ls.set_defaults(func=_cli_list)

    hp = sub.add_parser("help", help="Show interactive help for an entity.")
    hp.add_argument("name", nargs="?", default=None,
                    help="Entity to describe.")
    hp.add_argument("--kind", default=None, help="Narrow by kind.")
    hp.set_defaults(func=_cli_help)

    bd = sub.add_parser("build", help="Run the full pipeline (sims + site + PDF).")
    bd.add_argument("--out", default=None, help="Output directory.")
    bd.add_argument("--fast", action="store_true", help="Skip plot regeneration.")
    bd.add_argument("--skip-sims", action="store_true",
                    help="Skip simulation step; only refresh generators.")
    bd.add_argument("--only", default=None, help="Run only the step whose label "
                                                 "contains STEP (substring match).")
    bd.set_defaults(func=_cli_build)

    args = parser.parse_args(argv)
    return args.func(args)


__all__ = ["help", "cli"]
