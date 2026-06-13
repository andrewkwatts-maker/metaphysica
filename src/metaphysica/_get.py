"""Unified ``metaphysica.get()`` dispatcher.

The public-facing entry point. Resolves *name* to an :class:`EntityRef`
via the catalog, then dispatches to the appropriate format backend.

Sprint coverage
---------------

* **S1** (this file): ``json``, ``yaml``, ``latex`` for every entity
  kind that exposes data in those forms; ``GetJSON`` / ``GetYAML`` /
  ``GetLaTeX`` typed-alias wrappers.
* **S2**: triple-track — ``arithma``, ``eml``, ``float``.
* **S3**: image — ``svg``, ``png``.
* **S4**: document — ``pdf``, ``html``, ``md``.

Format strings can be passed either as plain ``str`` ("json") or as one
of the module-level constants (``metaphysica.JSON``); both forms are
``str``-subclass-compatible so callers can mix and match.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ._catalog import (
    KIND_CERTIFICATE,
    KIND_CONSTANT,
    KIND_DERIVATION,
    KIND_FORMULA,
    KIND_GATE,
    KIND_PARAMETER,
    KIND_PLOT,
    KIND_QUARK,
    KIND_REFERENCE,
    KIND_SECTION,
    KIND_SIMULATION,
    EntityRef,
    resolve,
)
from ._errors import MetaphysicaBackendError, MetaphysicaFormatError


# Format constants — str subclasses so they tab-complete in IDEs but also
# equality-compare cleanly against literal ``"json"`` etc.
class _Fmt(str):
    """Marker subclass so ``isinstance(fmt, str)`` stays True."""

    __slots__ = ()


JSON: _Fmt = _Fmt("json")
YAML: _Fmt = _Fmt("yaml")
LATEX: _Fmt = _Fmt("latex")
ARITHMA: _Fmt = _Fmt("arithma")
EML: _Fmt = _Fmt("eml")
FLOAT: _Fmt = _Fmt("float")
SVG: _Fmt = _Fmt("svg")
PNG: _Fmt = _Fmt("png")
PDF: _Fmt = _Fmt("pdf")
HTML: _Fmt = _Fmt("html")
MD: _Fmt = _Fmt("md")

#: Every format the dispatcher knows about (S1-S4 combined).
SUPPORTED_FORMATS: tuple = (
    "json", "yaml", "latex",
    "arithma", "eml", "float",
    "svg", "png",
    "pdf", "html", "md",
)


# Per-kind supported-format matrix. Entries are conservative — when a
# kind has *some* coverage for a format but the specific entity might
# not (e.g. parameters without arithma trees), the backend handles the
# missing-data case and raises a precise error.
_KIND_FORMATS: Dict[str, set] = {
    KIND_FORMULA: {"json", "yaml", "latex", "arithma", "eml", "float", "svg", "png", "html", "md"},
    # Numeric leaves: arithma + eml synthesise a "scalar(value)" view so
    # the format is uniformly available across triple-track exports.
    KIND_PARAMETER: {"json", "yaml", "latex", "arithma", "eml", "float", "md"},
    KIND_CONSTANT: {"json", "yaml", "latex", "arithma", "eml", "float", "md"},
    KIND_QUARK: {"json", "yaml", "latex", "arithma", "eml", "float", "md"},
    KIND_GATE: {"json", "yaml", "latex", "html", "md", "pdf"},
    KIND_CERTIFICATE: {"json", "yaml", "html", "md", "pdf"},
    KIND_SECTION: {"json", "yaml", "html", "md", "pdf"},
    KIND_PLOT: {"json", "yaml", "png", "pdf", "svg"},
    KIND_DERIVATION: {"json", "yaml", "md"},
    KIND_REFERENCE: {"json", "yaml", "md"},
    KIND_SIMULATION: {"json", "yaml"},
}


def get_supported_formats(name: str, *, kind: Optional[str] = None) -> list:
    """Return the sorted list of formats *name* supports."""
    ref = resolve(name, kind=kind)
    return sorted(_KIND_FORMATS.get(ref.kind, set()))


# ---------------------------------------------------------------------------
# Backend registry
# ---------------------------------------------------------------------------


_Backend = "callable[[EntityRef], Any]"


def _to_json(ref: EntityRef) -> Dict[str, Any]:
    """Backend for ``fmt='json'`` — return the parsed payload dict."""
    # Always return a fresh dict so callers can't mutate the cached ref.
    return dict(ref.payload)


def _to_yaml(ref: EntityRef) -> str:
    """Backend for ``fmt='yaml'`` — render the payload as YAML.

    Uses :mod:`yaml` (``pip install pyyaml``) if available; falls back
    to a minimal hand-rolled dumper otherwise so the lib doesn't
    hard-require PyYAML for the data-format leg.
    """
    payload = _to_json(ref)
    try:
        import yaml  # type: ignore

        return yaml.safe_dump(
            payload, default_flow_style=False, sort_keys=False, allow_unicode=True
        )
    except ImportError:
        return _yaml_fallback(payload)


def _yaml_fallback(obj: Any, indent: int = 0) -> str:
    """Tiny YAML serialiser for environments without PyYAML.

    Covers the subset the framework actually produces: nested dicts,
    lists of dicts, primitive leaves. Strings are quoted only when they
    contain YAML special characters. Good enough for the get() API; the
    user can pip-install pyyaml for full coverage.
    """
    pad = "  " * indent
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        lines = []
        for k, v in obj.items():
            ks = str(k)
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{ks}:")
                lines.append(_yaml_fallback(v, indent + 1))
            else:
                lines.append(f"{pad}{ks}: {_yaml_scalar(v, indent + 1)}")
        return "\n".join(lines)
    if isinstance(obj, list):
        if not obj:
            return "[]"
        lines = []
        for item in obj:
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{pad}-")
                lines.append(_yaml_fallback(item, indent + 1))
            else:
                lines.append(f"{pad}- {_yaml_scalar(item, indent + 1)}")
        return "\n".join(lines)
    return f"{pad}{_yaml_scalar(obj, indent)}"


def _yaml_scalar(v: Any, indent: int) -> str:
    """Render a scalar leaf for the fallback YAML dumper."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        if any(c in v for c in ":#-\n\"'[]{},&*?|<>=!%@`") or v != v.strip():
            # Quote and escape — minimal coverage.
            esc = v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            return f'"{esc}"'
        return v
    # Containers should not reach here — _yaml_fallback handles them.
    return repr(v)


def _to_latex(ref: EntityRef) -> str:
    """Backend for ``fmt='latex'`` — return the LaTeX render for the entity.

    Resolution order:
      1. ``payload['latex']`` for formulas / sections that carry it.
      2. ``payload['eml_latex']`` as fallback.
      3. ``payload['arithma_latex']`` when the formula has an Arithma view.
      4. A synthetic ``\\(value)\\) units`` form for numeric leaves
         (constants / parameters).
    """
    p = ref.payload
    if isinstance(p.get("latex"), str) and p["latex"].strip():
        return p["latex"]
    if isinstance(p.get("eml_latex"), str) and p["eml_latex"].strip():
        return p["eml_latex"]
    if isinstance(p.get("arithma_latex"), str) and p["arithma_latex"].strip():
        return p["arithma_latex"]
    # Synthetic fallback for numeric leaves.
    if ref.kind in (KIND_CONSTANT, KIND_PARAMETER):
        return _numeric_latex(p)
    raise MetaphysicaFormatError(
        ref.canonical_id, ref.kind, "latex",
        supported=_KIND_FORMATS.get(ref.kind, set()),
    )


def _numeric_latex(p: Dict[str, Any]) -> str:
    """Render ``value units`` as a LaTeX fragment for numeric leaves."""
    value = p.get("value")
    if value is None:
        value = p.get("computed") or p.get("predicted") or p.get("experimental_value")
    units = (
        (p.get("metadata") or {}).get("units")
        if isinstance(p.get("metadata"), dict)
        else None
    )
    units = units or p.get("units")
    name = p.get("symbol") or p.get("name") or p.get("label") or ""
    parts = []
    if name:
        parts.append(f"\\mathrm{{{name}}} = ")
    if value is None:
        parts.append("?")
    else:
        parts.append(_format_scientific_latex(value))
    if units:
        parts.append(f"\\,\\mathrm{{{units}}}")
    return "".join(parts)


def _format_scientific_latex(value: Any) -> str:
    """Format a number as LaTeX scientific notation when appropriate."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    if v == 0.0:
        return "0"
    abs_v = abs(v)
    if 1e-3 <= abs_v < 1e4:
        return f"{v:g}"
    # Use scientific notation
    mant, exp = f"{v:e}".split("e")
    mant = mant.rstrip("0").rstrip(".") or "0"
    return f"{mant}\\times 10^{{{int(exp)}}}"


# ---------------------------------------------------------------------------
# S2 — triple-track exports (Arithma symbolic / EML tree / Float)
# ---------------------------------------------------------------------------


def _to_arithma(ref: EntityRef) -> str:
    """Backend for ``fmt='arithma'`` — Arithma symbolic form as a string.

    Resolution order:
      1. ``payload['arithma_compact']`` (the symbolic AST) re-rendered
         as a compact prefix-form string when present and non-empty.
      2. ``payload['arithma_latex']`` (the LaTeX render of the Arithma
         expression).
      3. ``payload['eml_tree_str']`` as a near-equivalent fallback
         (Arithma and EML share the same algebraic primitives — both
         describe the formula's symbolic content, just with different
         conventions).
      4. ``MetaphysicaFormatError`` if the entity has no symbolic view
         at all (e.g. a pure-numeric constant).
    """
    p = ref.payload
    # Compact tree first — it's the most structured form.
    compact = p.get("arithma_compact")
    if compact:
        try:
            return _stringify_arithma_compact(compact)
        except Exception:
            pass
    latex = p.get("arithma_latex")
    if isinstance(latex, str) and latex.strip():
        return latex
    fallback = p.get("eml_tree_str")
    if isinstance(fallback, str) and fallback.strip():
        return fallback
    # For numeric leaves we can synthesise a trivial "scalar(value)" form.
    if ref.kind in (KIND_CONSTANT, KIND_PARAMETER):
        value = p.get("value")
        if value is not None:
            return f"scalar({value!r})"
    raise MetaphysicaFormatError(
        ref.canonical_id, ref.kind, "arithma",
        supported=_KIND_FORMATS.get(ref.kind, set()),
    )


def _stringify_arithma_compact(node: Any) -> str:
    """Render a compact Arithma tree (nested list/dict) as a prefix expression.

    The compact schema mirrors EML-Math's ``to_compact`` layout: each
    node is either a scalar (int/float/str) or a tagged list whose first
    element is the operator and remaining elements are operands. We
    walk it depth-first and emit ``op(arg, arg, ...)`` so the result is
    a readable, parser-friendly canonical form.
    """
    if isinstance(node, (int, float)):
        return repr(node)
    if isinstance(node, str):
        return node
    if isinstance(node, list) and node:
        op = str(node[0])
        args = ", ".join(_stringify_arithma_compact(a) for a in node[1:])
        return f"{op}({args})"
    if isinstance(node, dict):
        # Either {"op": "...", "args": [...]} or {"name": "...", "value": ...}.
        if "op" in node:
            args = ", ".join(_stringify_arithma_compact(a) for a in node.get("args", []))
            return f"{node['op']}({args})"
        if "name" in node and "value" in node:
            return f"{node['name']}({node['value']!r})"
        # Best-effort fallback.
        return repr(node)
    return repr(node)


def _to_eml(ref: EntityRef) -> Dict[str, Any]:
    """Backend for ``fmt='eml'`` — return the EML tree as a structured dict.

    Returns a dict with the canonical fields the rest of the framework
    consumes:

    ``{
        "tree_str": str,
        "tree_compact": <Any>,  # parsed JSON of the compact form
        "latex": str,
        "description": str,
        "value": float | None,
    }``

    Any field that is absent on the underlying entity is omitted from
    the returned dict so callers can ``.get()`` defensively without
    branching on schema versions.
    """
    p = ref.payload
    out: Dict[str, Any] = {}
    for src, dst in (
        ("eml_tree_str", "tree_str"),
        ("eml_latex", "latex"),
        ("eml_description", "description"),
        ("value", "value"),
    ):
        v = p.get(src)
        if v is not None and v != "":
            out[dst] = v
    # eml_tree_compact may be a JSON-serialised string or already a dict.
    compact = p.get("eml_tree_compact")
    if isinstance(compact, str) and compact.strip():
        try:
            out["tree_compact"] = json.loads(compact)
        except json.JSONDecodeError:
            out["tree_compact"] = compact
    elif compact is not None:
        out["tree_compact"] = compact

    # Numeric-leaf synthesis: constants / parameters / quarks don't
    # carry their own EML tree, but we can present their value as a
    # trivial eml_scalar node so callers can treat every entity
    # uniformly.
    if not out and ref.kind in (KIND_CONSTANT, KIND_PARAMETER, KIND_QUARK):
        value = p.get("value")
        if value is None and isinstance(p.get("pm_prediction"), dict):
            value = p["pm_prediction"].get("predicted_mass_GeV")
        if value is None:
            value = p.get("Mass_MeVc2")
        if value is not None:
            out["tree_str"] = f"eml_scalar({value!r})"
            out["tree_compact"] = ["scalar", value]
            out["value"] = float(value) if isinstance(value, (int, float)) else value

    if not out:
        raise MetaphysicaFormatError(
            ref.canonical_id, ref.kind, "eml",
            supported=_KIND_FORMATS.get(ref.kind, set()),
        )
    return out


def _to_float(ref: EntityRef) -> float:
    """Backend for ``fmt='float'`` — return the numeric value as a Python float.

    Constants and parameters expose their value directly. Formulas
    carry the evaluated triple-track value under ``payload['value']``.
    Sections / gates / certificates are non-numeric and raise.
    """
    p = ref.payload
    candidate = p.get("value")
    if candidate is None:
        candidate = p.get("computed") or p.get("predicted")
    if candidate is None and "experimental_value" in p:
        candidate = p["experimental_value"]
    if candidate is None:
        raise MetaphysicaFormatError(
            ref.canonical_id, ref.kind, "float",
            supported=_KIND_FORMATS.get(ref.kind, set()),
        )
    try:
        return float(candidate)
    except (TypeError, ValueError) as exc:
        # Non-numeric value (some entries carry strings like "see paper").
        raise MetaphysicaFormatError(
            ref.canonical_id, ref.kind, "float",
            supported=_KIND_FORMATS.get(ref.kind, set()),
        ) from exc


# ---------------------------------------------------------------------------
# S3 — image exports (SVG / PNG)
# ---------------------------------------------------------------------------

import re as _re


_SVG_BLOCK = _re.compile(r"<svg[^>]*>.*?</svg>", _re.DOTALL | _re.IGNORECASE)


def _extract_svg(html: str) -> Optional[str]:
    """Pull the first ``<svg>...</svg>`` block out of an HTML fragment."""
    if not isinstance(html, str):
        return None
    m = _SVG_BLOCK.search(html)
    return m.group(0) if m else None


def _to_svg(ref: EntityRef) -> str:
    """Backend for ``fmt='svg'`` — return an SVG XML fragment string.

    Resolution order:
      1. ``EntityRef.artefacts['svg']`` if a pre-rendered file is on disk
         (used by plots).
      2. ``payload['_renders']['svg']`` if the formula renders sidecar
         shipped a dedicated SVG.
      3. Extract ``<svg>`` from ``payload['_renders']['html']`` (formulas
         currently ship an HTML wrapper around the SVG).
      4. ``payload['svg']`` for any other entity that carries SVG inline.
      5. Raise :class:`MetaphysicaFormatError` with a hint pointing at
         ``metaphysica.build(out_dir=..., hq_pdf=True)``.
    """
    on_disk = ref.artefacts.get("svg")
    if isinstance(on_disk, Path) and on_disk.exists():
        return on_disk.read_text(encoding="utf-8")

    renders = ref.payload.get("_renders") if isinstance(ref.payload, dict) else None
    if isinstance(renders, dict):
        svg = renders.get("svg")
        if isinstance(svg, str) and svg.strip():
            return svg
        html_block = renders.get("html")
        if isinstance(html_block, str):
            inner = _extract_svg(html_block)
            if inner:
                return inner

    direct = ref.payload.get("svg") if isinstance(ref.payload, dict) else None
    if isinstance(direct, str) and direct.strip():
        return direct

    raise MetaphysicaFormatError(
        ref.canonical_id, ref.kind, "svg",
        supported=_KIND_FORMATS.get(ref.kind, set()),
    )


def _to_png(ref: EntityRef) -> bytes:
    """Backend for ``fmt='png'`` — return PNG bytes.

    Resolution order:
      1. ``EntityRef.artefacts['png']`` (plots + bundled curated images).
      2. ``payload['_renders']['png']`` if the formula renders sidecar
         carried a base64-encoded PNG.
      3. Plot manifest entry's ``file`` resolved against the plots dir.
      4. Raise :class:`MetaphysicaFormatError`.

    Note
    ----
    Formula PNG renders are not produced by the default build; they
    require ``metaphysica.build(..., hq_pdf=True)`` to spawn the
    playwright/Chromium renderer. We raise a precise error pointing at
    that flag rather than attempting a fragile JIT render here.
    """
    on_disk = ref.artefacts.get("png")
    if isinstance(on_disk, Path) and on_disk.exists():
        return on_disk.read_bytes()

    renders = ref.payload.get("_renders") if isinstance(ref.payload, dict) else None
    if isinstance(renders, dict):
        png = renders.get("png")
        if isinstance(png, str) and png.strip():
            # PNG in the renders sidecar is base64-encoded for JSON safety.
            import base64
            try:
                return base64.b64decode(png)
            except Exception:
                pass

    # Plot manifest may carry a relative file path under "file".
    if ref.kind == KIND_PLOT:
        file_field = ref.payload.get("file") if isinstance(ref.payload, dict) else None
        if isinstance(file_field, str):
            plots_dir = ref.source.parent / "plots"
            candidate = plots_dir / file_field
            if candidate.suffix.lower() != ".png":
                candidate = candidate.with_suffix(".png")
            if candidate.exists():
                return candidate.read_bytes()

    raise MetaphysicaFormatError(
        ref.canonical_id, ref.kind, "png",
        supported=_KIND_FORMATS.get(ref.kind, set()),
    )


# ---------------------------------------------------------------------------
# S4 — document exports (PDF / HTML / Markdown)
# ---------------------------------------------------------------------------


_TAG_STRIP = _re.compile(r"<[^>]+>")


def _strip_tags(html: str) -> str:
    """Crudely strip HTML tags for Markdown synthesis.

    The framework's section content is HTML with embedded
    ``<span class="pm-value" data-pm-value="...">`` placeholders. For
    Markdown we strip tags and collapse whitespace; we don't attempt
    full HTML-to-Markdown conversion (that's what generate_pdf_paper
    does on the server side).
    """
    text = _TAG_STRIP.sub("", html or "")
    return _re.sub(r"\s+\n\s+", "\n\n", _re.sub(r"[ \t]+", " ", text)).strip()


def _section_blocks(payload: Dict[str, Any]) -> list:
    """Return the section's content blocks (handles snake- and camelCase)."""
    blocks = payload.get("contentBlocks") or payload.get("content_blocks") or []
    return blocks if isinstance(blocks, list) else []


def _to_html(ref: EntityRef) -> str:
    """Backend for ``fmt='html'`` — return a self-contained HTML fragment.

    For sections, concatenates ``contentBlocks[*].content`` with each
    block wrapped in ``<div class="pm-block" data-type="...">``.
    For gates / certificates, synthesises a small HTML card from the
    JSON metadata. For formulas, returns ``payload['_renders']['html']``
    when available.
    """
    p = ref.payload if isinstance(ref.payload, dict) else {}

    # Formulas: re-use the pre-rendered HTML when available.
    if ref.kind == KIND_FORMULA:
        renders = p.get("_renders")
        if isinstance(renders, dict):
            html = renders.get("html")
            if isinstance(html, str) and html.strip():
                return html
        # Fall back to a synthetic card from the JSON.
        title = p.get("title") or p.get("label") or ref.canonical_id
        latex = p.get("latex") or p.get("eml_latex") or ""
        desc = p.get("description") or p.get("plain_text") or ""
        return (
            f'<div class="pm-formula" data-id="{ref.canonical_id}">\n'
            f'  <h3>{title}</h3>\n'
            f'  <div class="pm-latex">$${latex}$$</div>\n'
            f'  <p class="pm-desc">{desc}</p>\n'
            f'</div>'
        )

    if ref.kind == KIND_SECTION:
        blocks = _section_blocks(p)
        title = p.get("title") or p.get("label") or ref.canonical_id
        parts = [
            f'<section class="pm-section" data-id="{ref.canonical_id}">',
            f'  <h2>{title}</h2>',
        ]
        for b in blocks:
            if not isinstance(b, dict):
                continue
            btype = b.get("type") or "paragraph"
            label = b.get("label") or b.get("equationNumber") or ""
            content = b.get("content") or ""
            parts.append(
                f'  <div class="pm-block" data-type="{btype}" data-label="{label}">'
                f'{content}</div>'
            )
        parts.append("</section>")
        return "\n".join(parts)

    if ref.kind in (KIND_GATE, KIND_CERTIFICATE):
        title = p.get("title") or p.get("name") or p.get("label") or ref.canonical_id
        status = p.get("status") or p.get("verdict") or ""
        notes = p.get("notes") or p.get("description") or ""
        return (
            f'<article class="pm-{ref.kind}" data-id="{ref.canonical_id}">\n'
            f'  <h3>{title}</h3>\n'
            f'  <p class="pm-status">Status: <strong>{status}</strong></p>\n'
            f'  <p class="pm-notes">{notes}</p>\n'
            f'</article>'
        )

    raise MetaphysicaFormatError(
        ref.canonical_id, ref.kind, "html",
        supported=_KIND_FORMATS.get(ref.kind, set()),
    )


def _to_md(ref: EntityRef) -> str:
    """Backend for ``fmt='md'`` — return a Markdown rendering.

    Synthesises from the JSON payload so every entity kind can support
    Markdown export uniformly (no extra runtime dependencies).
    """
    p = ref.payload if isinstance(ref.payload, dict) else {}

    if ref.kind == KIND_SECTION:
        blocks = _section_blocks(p)
        title = p.get("title") or p.get("label") or ref.canonical_id
        out = [f"# {title}", ""]
        for b in blocks:
            if not isinstance(b, dict):
                continue
            btype = (b.get("type") or "paragraph").lower()
            content = _strip_tags(b.get("content") or "")
            if not content:
                continue
            if btype == "heading":
                out.append(f"## {content}")
            elif btype in ("formula", "equation"):
                out.append(f"$$ {content} $$")
            elif btype == "list":
                out.append(content)
            else:
                out.append(content)
            out.append("")
        return "\n".join(out).rstrip() + "\n"

    if ref.kind == KIND_FORMULA:
        title = p.get("title") or p.get("label") or ref.canonical_id
        latex = p.get("latex") or p.get("eml_latex") or ""
        desc = _strip_tags(p.get("description") or p.get("plain_text") or "")
        value = p.get("value")
        lines = [f"# {title}", "", f"**ID:** `{ref.canonical_id}`", ""]
        if latex:
            lines.extend([f"$$ {latex} $$", ""])
        if desc:
            lines.extend([desc, ""])
        if value is not None:
            lines.append(f"**Numeric value:** `{value}`")
        return "\n".join(lines).rstrip() + "\n"

    if ref.kind in (KIND_CONSTANT, KIND_PARAMETER, KIND_QUARK):
        name = (
            p.get("name")
            or p.get("Name")
            or p.get("symbol")
            or ref.canonical_id
        )
        value = p.get("value") or p.get("Mass_MeVc2")
        units = (
            (p.get("metadata") or {}).get("units")
            if isinstance(p.get("metadata"), dict)
            else None
        ) or p.get("units")
        desc = (
            ((p.get("metadata") or {}).get("description")
             if isinstance(p.get("metadata"), dict) else None)
            or p.get("description")
            or ""
        )
        lines = [f"# {name}", "", f"**ID:** `{ref.canonical_id}`", ""]
        if value is not None:
            lines.append(f"**Value:** `{value}`" + (f" {units}" if units else ""))
        if desc:
            lines.extend(["", desc])
        return "\n".join(lines).rstrip() + "\n"

    if ref.kind in (KIND_GATE, KIND_CERTIFICATE):
        title = p.get("title") or p.get("name") or p.get("label") or ref.canonical_id
        status = p.get("status") or p.get("verdict") or "unknown"
        notes = _strip_tags(p.get("notes") or p.get("description") or "")
        lines = [f"# {title}", "", f"**ID:** `{ref.canonical_id}`", "", f"**Status:** {status}"]
        if notes:
            lines.extend(["", notes])
        return "\n".join(lines).rstrip() + "\n"

    if ref.kind in (KIND_DERIVATION, KIND_REFERENCE):
        title = p.get("title") or p.get("label") or ref.canonical_id
        body = _strip_tags(
            p.get("content")
            or p.get("description")
            or p.get("abstract")
            or ""
        )
        lines = [f"# {title}", ""]
        if body:
            lines.append(body)
        return "\n".join(lines).rstrip() + "\n"

    raise MetaphysicaFormatError(
        ref.canonical_id, ref.kind, "md",
        supported=_KIND_FORMATS.get(ref.kind, set()),
    )


def _to_pdf(ref: EntityRef) -> bytes:
    """Backend for ``fmt='pdf'`` — return PDF bytes.

    Resolution order:
      1. ``EntityRef.artefacts['pdf']`` for plots (pre-rendered).
      2. The bundled full paper PDF for sections — sections currently
         resolve to the same paper PDF; an opt-in
         ``slice_section=True`` opt could split it per-section in a
         future sprint (S4 keeps it whole-document for now).
      3. Raise with a hint pointing at ``metaphysica.build(hq_pdf=True)``.
    """
    on_disk = ref.artefacts.get("pdf")
    if isinstance(on_disk, Path) and on_disk.exists():
        return on_disk.read_bytes()

    # Sections fall back to the full paper PDF when present.
    if ref.kind == KIND_SECTION:
        paper = ref.source.parent / "Principia_Metaphysica_Paper.pdf"
        if paper.exists():
            return paper.read_bytes()

    # Plot manifest entry may carry a relative file path under "file".
    if ref.kind == KIND_PLOT:
        file_field = ref.payload.get("file") if isinstance(ref.payload, dict) else None
        if isinstance(file_field, str):
            plots_dir = ref.source.parent / "plots"
            candidate = plots_dir / file_field
            if candidate.suffix.lower() != ".pdf":
                candidate = candidate.with_suffix(".pdf")
            if candidate.exists():
                return candidate.read_bytes()

    raise MetaphysicaFormatError(
        ref.canonical_id, ref.kind, "pdf",
        supported=_KIND_FORMATS.get(ref.kind, set()),
    )


# S1+S2+S3+S4 — complete backend dispatch table.
_BACKENDS: Dict[str, _Backend] = {
    "json": _to_json,
    "yaml": _to_yaml,
    "latex": _to_latex,
    "arithma": _to_arithma,
    "eml": _to_eml,
    "float": _to_float,
    "svg": _to_svg,
    "png": _to_png,
    "html": _to_html,
    "md": _to_md,
    "pdf": _to_pdf,
}


# ---------------------------------------------------------------------------
# Public dispatcher
# ---------------------------------------------------------------------------


def get(
    name: str,
    fmt: Union[str, _Fmt] = JSON,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> Any:
    """Retrieve *name* in format *fmt*.

    Parameters
    ----------
    name
        Lookup key. Resolved across the unified catalog (formulas,
        parameters, gates, particles, sections, plots, ...).
    fmt
        One of ``json`` / ``yaml`` / ``latex`` / ``arithma`` / ``eml``
        / ``float`` / ``svg`` / ``png`` / ``pdf`` / ``html`` / ``md``,
        either as a literal string or via the module-level constants
        (``metaphysica.JSON``, ``metaphysica.PNG``, ...).
    kind
        Optional narrowing: ``constant`` / ``parameter`` / ``formula``
        / ``gate`` / ``certificate`` / ``section`` / ``plot`` /
        ``quark`` / ``derivation`` / ``reference`` / ``simulation``.
        Use when a bare name resolves ambiguously.
    out_path
        If supplied, also write the result to this path (creates parent
        dirs). The in-memory value is still returned. Text formats use
        UTF-8; binary formats (PNG/PDF) write bytes verbatim.
    **opts
        Format-specific kwargs (e.g. ``include_derivation=True`` for
        formula JSON; reserved for S2-S4).

    Returns
    -------
    object
        Return type follows the format contract:

        * ``json``  → ``dict``
        * ``yaml`` / ``latex`` / ``arithma`` / ``svg`` / ``html`` / ``md``
          → ``str``
        * ``eml`` → ``dict``
        * ``float`` → ``float``
        * ``png`` / ``pdf`` → ``bytes``

    Raises
    ------
    MetaphysicaKeyError
        *name* does not match any catalog entry.
    MetaphysicaAmbiguityError
        *name* matches more than one kind; pass ``kind=`` to disambiguate.
    MetaphysicaFormatError
        *fmt* is not supported for the resolved entity's kind, or is not
        recognised at all.
    """
    fmt_key = str(fmt).lower()
    if fmt_key not in SUPPORTED_FORMATS:
        raise MetaphysicaFormatError(
            name, kind or "?", fmt_key, supported=SUPPORTED_FORMATS
        )

    ref = resolve(name, kind=kind)

    # Per-kind format guard — fast-fail with a precise error if the user
    # asks for e.g. PNG of a constant.
    allowed = _KIND_FORMATS.get(ref.kind, set())
    if fmt_key not in allowed:
        raise MetaphysicaFormatError(
            ref.canonical_id, ref.kind, fmt_key, supported=allowed
        )

    backend = _BACKENDS.get(fmt_key)
    if backend is None:
        # Format is in SUPPORTED_FORMATS but no S1-time backend yet
        # (S2-S4 territory). Tell the caller plainly.
        raise MetaphysicaFormatError(
            ref.canonical_id,
            ref.kind,
            fmt_key,
            supported=sorted(_BACKENDS.keys()),
        )

    try:
        result = backend(ref)
    except (MetaphysicaFormatError, KeyError, AttributeError):
        raise
    except Exception as exc:
        raise MetaphysicaBackendError(ref.canonical_id, fmt_key, exc) from exc

    if out_path is not None:
        _write_out(result, fmt_key, Path(out_path), ref.canonical_id)
    return result


def _write_out(value: Any, fmt_key: str, dest: Path, canonical_id: str) -> None:
    """Persist *value* to *dest* using the right text/binary mode for *fmt_key*.

    When *dest* is an existing directory, auto-names the file
    ``<canonical_id>.<ext>``.
    """
    if dest.is_dir():
        safe_id = canonical_id.replace("/", "_").replace("\\", "_")
        dest = dest / f"{safe_id}.{fmt_key}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, (bytes, bytearray)):
        dest.write_bytes(bytes(value))
        return
    if fmt_key == "json" and isinstance(value, dict):
        dest.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        return
    if isinstance(value, (int, float)):
        dest.write_text(repr(value), encoding="utf-8")
        return
    if isinstance(value, dict):
        dest.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
        return
    dest.write_text(str(value), encoding="utf-8")


# ---------------------------------------------------------------------------
# Typed alias wrappers — thin, IDE-discoverable, identical semantics.
# ---------------------------------------------------------------------------


def GetJSON(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> Dict[str, Any]:
    """Return *name* as a JSON-shaped ``dict``. See :func:`get`."""
    return get(name, JSON, kind=kind, out_path=out_path, **opts)


def GetYAML(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> str:
    """Return *name* as a YAML string. See :func:`get`."""
    return get(name, YAML, kind=kind, out_path=out_path, **opts)


def GetLaTeX(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> str:
    """Return *name* as a LaTeX fragment string. See :func:`get`."""
    return get(name, LATEX, kind=kind, out_path=out_path, **opts)


def GetArithma(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> str:
    """Return *name*'s Arithma symbolic form as a string. See :func:`get`."""
    return get(name, ARITHMA, kind=kind, out_path=out_path, **opts)


def GetEML(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> Dict[str, Any]:
    """Return *name*'s EML tree as a structured dict. See :func:`get`."""
    return get(name, EML, kind=kind, out_path=out_path, **opts)


def GetFloat(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> float:
    """Return *name*'s numeric value as a Python ``float``. See :func:`get`."""
    return get(name, FLOAT, kind=kind, out_path=out_path, **opts)


def GetSVG(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> str:
    """Return *name* as an SVG XML string. See :func:`get`."""
    return get(name, SVG, kind=kind, out_path=out_path, **opts)


def GetPNG(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> bytes:
    """Return *name*'s PNG render as raw ``bytes``. See :func:`get`."""
    return get(name, PNG, kind=kind, out_path=out_path, **opts)


def GetPDF(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> bytes:
    """Return *name*'s PDF render as raw ``bytes``. See :func:`get`."""
    return get(name, PDF, kind=kind, out_path=out_path, **opts)


def GetHTML(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> str:
    """Return *name* as an HTML fragment string. See :func:`get`."""
    return get(name, HTML, kind=kind, out_path=out_path, **opts)


def GetMarkdown(
    name: str,
    *,
    kind: Optional[str] = None,
    out_path: Optional[Union[str, Path]] = None,
    **opts: Any,
) -> str:
    """Return *name* as a Markdown document string. See :func:`get`."""
    return get(name, MD, kind=kind, out_path=out_path, **opts)


__all__ = [
    "get",
    "GetJSON",
    "GetYAML",
    "GetLaTeX",
    "GetArithma",
    "GetEML",
    "GetFloat",
    "GetSVG",
    "GetPNG",
    "GetPDF",
    "GetHTML",
    "GetMarkdown",
    "JSON",
    "YAML",
    "LATEX",
    "ARITHMA",
    "EML",
    "FLOAT",
    "SVG",
    "PNG",
    "PDF",
    "HTML",
    "MD",
    "SUPPORTED_FORMATS",
    "get_supported_formats",
]
