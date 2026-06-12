"""Codemod: inject ``b3_leaf()`` into Formula constructors whose
``eml_tree_str`` (or ``eml_description``) references ``topology.elder_kads``
as an input but encodes ``b_3`` as the bare literal ``24`` / ``24.0``
(typically ``eml_scalar(24.0)`` or ``eml_scalar(24)``).

Reference: ``TIER_2_3_ROADMAP.md §T4.1`` -- 18 (b) "missing chain link"
residuals identified by ``NON_B3_INVENTORY.md`` after T2/T3 sweeps.

Approach
--------
1. Walk every ``.py`` file under ``src/metaphysica/simulations/PM/**``.
2. Find each ``Formula(`` constructor block via brace-balanced slicing.
3. For each block where ``input_params`` (or ``inputParams``) contains
   ``"topology.elder_kads"``:
     * Extract the ``eml_tree_str=`` and ``eml_description=`` argument
       text.
     * If either text already contains the literal token ``b3_leaf``,
       skip -- it's already rooted.
     * Otherwise, scan for ``eml_scalar(24)`` or ``eml_scalar(24.0)``
       occurrences. Each such occurrence is a candidate for replacement
       with ``b3_leaf()``.
4. Emit ``scripts/_codemod_b3_leaf_inject_proposed.json`` with the full
   proposal payload: file path, formula id, line range, before/after
   snippet pairs, and replacement count.

The script is *propose-only* by default. Pass ``--apply`` to rewrite the
files in place (writes a ``.bak`` next to each modified source). Default
behaviour exits 0 even when proposals exist; ``--strict`` makes it exit 1
if any proposals are emitted (useful as a CI gate after manual review).

Usage
-----
::

    python scripts/codemod_b3_leaf_inject.py            # propose only
    python scripts/codemod_b3_leaf_inject.py --apply    # rewrite in place
    python scripts/codemod_b3_leaf_inject.py --strict   # CI exit 1 mode
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
PM_ROOT = REPO_ROOT / "src" / "metaphysica" / "simulations" / "PM"
OUTPUT_JSON = REPO_ROOT / "scripts" / "_codemod_b3_leaf_inject_proposed.json"

# The (b) residual formula IDs from NON_B3_INVENTORY.md. Used for
# annotation only -- the codemod itself is structural, not id-driven --
# so a (b) residual id is added to each proposal so reviewers can match
# them up against the inventory. Unknown ids still get proposed; they
# are flagged ``inventory_match=False``.
B_RESIDUAL_IDS = frozenset({
    # cosmology
    "bounce-action-v19",
    "dark-energy-eos",
    "hubble-tension-resolution",
    "moduli-damping-v18",
    "s8-definition",
    "tunneling-rate-v19",
    "vacuum-lifetime-v19",
    # field_dynamics
    "shadow-torsion-sum",
    # gauge
    "gauge-coupling-unification",
    "gut-scale",
    "instability-scale-v19",
    "kk-threshold",
    # geometry
    "c-torsion-derivation",
    "calabi-yau-projection",
    "torsion-funnel-exit",
    # particle
    "higgs-brane-projection",
    "mass-spectrum-v18",
    # portals
    "axion-decay-constant-v18",
})

# Match eml_scalar(24) or eml_scalar(24.0) (with optional whitespace).
# We treat both as the literal b_3 = 24 token. Float forms like
# eml_scalar(24.00) or eml_scalar(2.4e1) are out of scope; the inventory
# does not cite any.
SCALAR_24_RX = re.compile(r"eml_scalar\(\s*24(?:\.0+)?\s*\)")
# Bare ``24`` / ``24.0`` literal not wrapped in eml_scalar -- this is
# rarer but does occur in eml_description comments. We only flag it
# inside eml_tree_str.
BARE_24_RX = re.compile(r"(?<![\w.])24(?:\.0+)?(?![\w.])")
ID_RX = re.compile(r"\bid\s*=\s*['\"]([\w\-.]+)['\"]")


@dataclass
class FormulaProposal:
    file: str
    formula_id: str
    inventory_match: bool
    line_start: int
    line_end: int
    eml_tree_str_present: bool
    eml_description_present: bool
    scalar_24_hits: int
    bare_24_hits_in_tree: int
    diff_eml_tree_str: List[Dict[str, str]] = field(default_factory=list)
    diff_eml_description: List[Dict[str, str]] = field(default_factory=list)
    notes: str = ""


def _find_formula_blocks(source: str) -> List[Tuple[int, int, int, int]]:
    """Return ``(start_off, end_off, start_line, end_line)`` for every
    ``Formula(`` constructor block in *source*. Brace-balances on the
    outer parens. End offset is one past the closing paren.
    """
    blocks: List[Tuple[int, int, int, int]] = []
    i = 0
    n = len(source)
    needle = "Formula("
    while True:
        j = source.find(needle, i)
        if j < 0:
            break
        # Skip class definitions / type hints / list comprehensions
        # that just reference ``Formula``: we only want a call where the
        # next non-space char after Formula( starts an arg list. Easiest
        # filter: the char immediately before "Formula" must not be an
        # identifier char (so we don't match ``MyFormula(``).
        if j > 0 and (source[j - 1].isalnum() or source[j - 1] == "_"):
            i = j + len(needle)
            continue
        start = j
        depth = 0
        k = j + len(needle) - 1  # position of the '('
        while k < n:
            c = source[k]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
            elif c == "#":
                nl = source.find("\n", k)
                k = n if nl < 0 else nl
                continue
            elif c in ("'", '"'):
                # Skip string literal (handle triple-quoted)
                triple = source[k:k + 3] in ('"""', "'''")
                if triple:
                    quote = source[k:k + 3]
                    end = source.find(quote, k + 3)
                    k = n if end < 0 else end + 3
                    continue
                else:
                    quote = c
                    m = k + 1
                    while m < n:
                        if source[m] == "\\":
                            m += 2
                            continue
                        if source[m] == quote:
                            m += 1
                            break
                        m += 1
                    k = m
                    continue
            k += 1
        if depth != 0:
            # Unbalanced -- stop scanning, malformed file.
            break
        end = k + 1
        start_line = source.count("\n", 0, start) + 1
        end_line = source.count("\n", 0, end) + 1
        blocks.append((start, end, start_line, end_line))
        i = end
    return blocks


def _extract_kwarg(block_src: str, name: str) -> Optional[Tuple[int, int, str]]:
    """Return ``(value_start, value_end, value_src)`` for the kwarg
    ``name=`` inside *block_src*. None if absent. Value extent ends
    where a top-level comma or the final ``)`` appears.
    """
    rx = re.compile(rf"\b{name}\s*=")
    m = rx.search(block_src)
    if not m:
        return None
    i = m.end()
    n = len(block_src)
    depth = 0
    val_start = i
    # Walk forward, brace-tracking, until we hit a comma at depth 0 or
    # the outer closing paren (depth would go negative on outer ``)``).
    while i < n:
        c = block_src[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                break
            depth -= 1
        elif c == "," and depth == 0:
            break
        elif c == "#":
            nl = block_src.find("\n", i)
            i = n if nl < 0 else nl
            continue
        elif c in ("'", '"'):
            triple = block_src[i:i + 3] in ('"""', "'''")
            if triple:
                quote = block_src[i:i + 3]
                end = block_src.find(quote, i + 3)
                i = n if end < 0 else end + 3
                continue
            else:
                quote = c
                m2 = i + 1
                while m2 < n:
                    if block_src[m2] == "\\":
                        m2 += 2
                        continue
                    if block_src[m2] == quote:
                        m2 += 1
                        break
                    m2 += 1
                i = m2
                continue
        i += 1
    val_end = i
    return (val_start, val_end, block_src[val_start:val_end])


def _formula_uses_elder_kads(block_src: str) -> bool:
    """Return True iff any input_params / inputParams kwarg lists
    ``"topology.elder_kads"``."""
    for name in ("input_params", "inputParams"):
        ext = _extract_kwarg(block_src, name)
        if ext is None:
            continue
        _, _, val = ext
        if "topology.elder_kads" in val:
            return True
    return False


def _formula_id(block_src: str) -> str:
    m = ID_RX.search(block_src)
    return m.group(1) if m else "<unknown>"


def _propose_for_text(text: str) -> Tuple[List[Dict[str, str]], int]:
    """Return ``(diff_pairs, total_hits)`` for *text*: every
    ``eml_scalar(24[.0])`` becomes ``b3_leaf()``. We surface each unique
    surrounding fragment as a before/after pair so a reviewer can see
    the local context. ``b3_leaf`` is the symbolic primitive defined in
    the EML-Math primitive registry -- the same one used by the manual
    T2.3 fix in ``multi_sector.py`` (formula ``dark-energy-eos``).
    """
    diff_pairs: List[Dict[str, str]] = []
    hits = list(SCALAR_24_RX.finditer(text))
    if not hits:
        return ([], 0)
    seen = set()
    for m in hits:
        # Build a small surrounding fragment for reviewer context
        lo = max(0, m.start() - 32)
        hi = min(len(text), m.end() + 32)
        before = text[lo:hi]
        after = text[lo:m.start()] + "b3_leaf()" + text[m.end():hi]
        key = (before, after)
        if key in seen:
            continue
        seen.add(key)
        diff_pairs.append({"before": before, "after": after})
    return (diff_pairs, len(hits))


def _apply_to_text(text: str) -> str:
    return SCALAR_24_RX.sub("b3_leaf()", text)


def analyse_file(path: Path) -> List[FormulaProposal]:
    source = path.read_text(encoding="utf-8")
    if "Formula(" not in source or "topology.elder_kads" not in source:
        return []

    proposals: List[FormulaProposal] = []
    for start, end, ln_start, ln_end in _find_formula_blocks(source):
        block = source[start:end]
        if not _formula_uses_elder_kads(block):
            continue

        # Pull the two text fields we care about
        tree_ext = _extract_kwarg(block, "eml_tree_str")
        desc_ext = _extract_kwarg(block, "eml_description")

        tree_text = tree_ext[2] if tree_ext else ""
        desc_text = desc_ext[2] if desc_ext else ""

        # If b3_leaf is already mentioned anywhere in either field,
        # the formula is already manually rooted -- skip.
        if "b3_leaf" in tree_text or "b3_leaf" in desc_text:
            continue

        diff_tree, tree_hits = _propose_for_text(tree_text)
        diff_desc, desc_hits = _propose_for_text(desc_text)

        # Count bare literal `24` occurrences in eml_tree_str for
        # reviewer awareness (we do NOT auto-rewrite bare 24 because
        # it could be a coincident numeric -- e.g. ``ops.div(x, 24)``
        # inside a comment block).
        bare_in_tree = 0
        if tree_text:
            # Avoid double-counting bare 24 inside eml_scalar(24...) --
            # SCALAR_24_RX already covers those, so subtract them.
            bare_in_tree = len(BARE_24_RX.findall(tree_text)) - tree_hits

        if tree_hits == 0 and desc_hits == 0:
            # Nothing actionable: no eml_scalar(24) anywhere. We still
            # surface it as a manual review proposal if the bare-24
            # count is positive, since the formula matches the
            # "elder_kads input but no b3_leaf" trigger condition.
            if bare_in_tree <= 0:
                continue
            note = (
                "no eml_scalar(24) candidates -- manual review for bare "
                f"`24` literal in eml_tree_str ({bare_in_tree} hit(s))"
            )
        else:
            note = (
                f"auto-suggest eml_scalar(24[.0]) -> b3_leaf() "
                f"({tree_hits} tree, {desc_hits} description)"
            )

        fid = _formula_id(block)
        proposals.append(FormulaProposal(
            file=str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
            formula_id=fid,
            inventory_match=fid in B_RESIDUAL_IDS,
            line_start=ln_start,
            line_end=ln_end,
            eml_tree_str_present=tree_ext is not None,
            eml_description_present=desc_ext is not None,
            scalar_24_hits=tree_hits + desc_hits,
            bare_24_hits_in_tree=max(0, bare_in_tree),
            diff_eml_tree_str=diff_tree,
            diff_eml_description=diff_desc,
            notes=note,
        ))
    return proposals


def apply_file(path: Path) -> int:
    """Rewrite *path* in-place: every ``eml_scalar(24[.0])`` inside a
    Formula() block whose ``input_params`` mentions ``topology.elder_kads``
    and whose existing eml_tree_str/eml_description does not already
    contain ``b3_leaf`` becomes ``b3_leaf()``. Returns the total number
    of replacements performed.
    """
    source = path.read_text(encoding="utf-8")
    if "Formula(" not in source or "topology.elder_kads" not in source:
        return 0
    blocks = _find_formula_blocks(source)
    # Process in reverse so offsets stay valid as we splice.
    total = 0
    new_source = source
    for start, end, _ln_s, _ln_e in reversed(blocks):
        block = new_source[start:end]
        if not _formula_uses_elder_kads(block):
            continue
        tree_ext = _extract_kwarg(block, "eml_tree_str")
        desc_ext = _extract_kwarg(block, "eml_description")
        tree_text = tree_ext[2] if tree_ext else ""
        desc_text = desc_ext[2] if desc_ext else ""
        if "b3_leaf" in tree_text or "b3_leaf" in desc_text:
            continue

        new_block = block
        # Apply substitutions to whichever fields exist. We only touch
        # the *value spans* (tree_ext / desc_ext slices into block) so
        # surrounding kwargs are not perturbed.
        for ext in (desc_ext, tree_ext):  # rewrite desc first to keep tree offsets valid -- both spans are within the block, reverse-sort applies
            if ext is None:
                continue
            v_start, v_end, v_text = ext
            new_v = _apply_to_text(v_text)
            if new_v == v_text:
                continue
            total += len(SCALAR_24_RX.findall(v_text))
            new_block = new_block[:v_start] + new_v + new_block[v_end:]
            # Refresh the *other* ext if its span shifted (only if desc
            # came before tree in block -- conservative: re-extract).
            if ext is desc_ext and tree_ext is not None:
                tree_ext = _extract_kwarg(new_block, "eml_tree_str")
        new_source = new_source[:start] + new_block + new_source[end:]

    if new_source != source:
        bak = path.with_suffix(path.suffix + ".bak")
        bak.write_text(source, encoding="utf-8")
        path.write_text(new_source, encoding="utf-8")
    return total


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--apply",
        action="store_true",
        help="rewrite source files in place (writes .bak backups)",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any proposals are emitted (CI gate)",
    )
    ap.add_argument(
        "--root",
        type=Path,
        default=PM_ROOT,
        help=f"package root to walk (default: {PM_ROOT})",
    )
    args = ap.parse_args(argv)

    if not args.root.exists():
        print(f"error: package root not found: {args.root}", file=sys.stderr)
        return 2

    py_files = sorted(args.root.rglob("*.py"))
    print(f"[codemod] scanning {len(py_files)} .py files under {args.root}")

    all_proposals: List[FormulaProposal] = []
    files_seen = 0
    for path in py_files:
        try:
            props = analyse_file(path)
        except Exception as exc:
            print(f"[codemod] WARN failed to analyse {path}: {exc}", file=sys.stderr)
            continue
        if props:
            files_seen += 1
            all_proposals.extend(props)

    applied = 0
    if args.apply and all_proposals:
        for path in {REPO_ROOT / p.file for p in all_proposals}:
            applied += apply_file(path)

    summary = {
        "tool": "codemod_b3_leaf_inject",
        "version": "1.0.0",
        "root": str(args.root).replace("\\", "/"),
        "files_scanned": len(py_files),
        "files_with_proposals": files_seen,
        "total_proposals": len(all_proposals),
        "total_scalar_24_hits": sum(p.scalar_24_hits for p in all_proposals),
        "applied": args.apply,
        "applied_replacements": applied,
        "b_residual_ids_expected": sorted(B_RESIDUAL_IDS),
        "proposals": [asdict(p) for p in all_proposals],
    }

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"[codemod] {len(all_proposals)} proposals across {files_seen} files "
        f"-> {OUTPUT_JSON.relative_to(REPO_ROOT)}"
    )

    # Bucket counts for quick human triage
    by_file: Dict[str, int] = {}
    inv_match = 0
    for p in all_proposals:
        by_file[p.file] = by_file.get(p.file, 0) + 1
        if p.inventory_match:
            inv_match += 1
    if by_file:
        print(f"[codemod] inventory matches: {inv_match} / {len(all_proposals)}")
        for fp, count in sorted(by_file.items(), key=lambda kv: -kv[1]):
            print(f"  {count:>3}  {fp}")

    if args.strict and all_proposals:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
