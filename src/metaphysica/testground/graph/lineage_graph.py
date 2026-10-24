"""Lineage in the path graph: version nodes, their edges, declared-only switches.

Generic: it reads a `Lineage` (see `metaphysica.testground.lineage`) and
never knows which theory it belongs to. Declared-only forks and options become
ordinary `Fork` / `VariantOption` objects with ``implemented=False``, so the
switches view draws them like any other (class ``not_implemented``).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Mapping, Optional

from metaphysica.testground.lineage.model import (DeclaredFork,
                                                  DeclaredOption, Lineage,
                                                  Version)
from metaphysica.testground.switches.model import (CERTAIN, CONSIDERED,
                                                   DISABLED, Fork,
                                                   VariantOption)

__all__ = ["version_node_id", "declared_option", "declared_fork",
           "merge_declared", "add_lineage"]


def version_node_id(version_id: str) -> str:
    return "version:%s" % version_id


def declared_option(o: DeclaredOption) -> VariantOption:
    """A catalogue option as an unimplemented switch option."""
    consequence = o.consequence
    if o.source and o.source != o.restored_from:
        consequence = (consequence + "\nSource: " + o.source).strip()
    refuted = o.status in ("disabled", "rejected")
    return VariantOption(
        id=o.id, summary=o.summary, consequence=consequence,
        status=DISABLED if refuted else CONSIDERED,
        certainty=CERTAIN if o.status == "rejected" else None,
        implemented=False, restored_from=o.restored_from,
        kill_condition=o.kill_condition, decision_refs=o.decision_refs)


def declared_fork(f: DeclaredFork) -> Fork:
    return Fork(id=f.id, question=f.question, source=f.source, options=[],
                status="declared", notes=f.notes)


def merge_declared(forks: Mapping[str, Fork], lineage: Optional[Lineage]
                   ) -> Dict[str, Fork]:
    """``forks`` plus the catalogue's declared forks and options.

    Idempotent: an option the fork already has is left alone.
    """
    out: Dict[str, Fork] = dict(forks)
    if lineage is None:
        return out
    for f in lineage.forks:
        out.setdefault(f.id, declared_fork(f))
    for o in lineage.options:
        fork = out[o.fork]
        if o.id not in fork.option_ids():
            out[o.fork] = dataclasses.replace(
                fork, options=list(fork.options) + [declared_option(o)])
    return out


def _version_attrs(v: Version, era_order: int) -> Dict[str, Any]:
    attrs = dataclasses.asdict(v)
    attrs.pop("id")
    attrs["era_order"] = era_order
    return attrs


def _sections(v: Version) -> List[Dict[str, str]]:
    out = []
    for key, heading, items in (("worked", "What worked", v.worked),
                                ("failed", "What failed", v.failed)):
        if items:
            out.append({"key": key, "heading": heading,
                        "body": "\n".join("- " + s for s in items)})
    return out


def _version_node(v: Version, era_order: int) -> Dict[str, Any]:
    return {"id": version_node_id(v.id), "type": "version", "label": v.label,
            "status": v.status, "class": v.status,
            "attrs": _version_attrs(v, era_order),
            "rationale": {"summary": v.why, "sections": _sections(v)}}


def _add_edges(b: Any, lineage: Lineage, option_ids: set) -> None:
    status = {v.id: v.status for v in lineage.versions}
    for v in lineage.versions:
        if v.parent:
            b.edge("evolves_to", version_node_id(v.parent),
                   version_node_id(v.id), v.status)
        if v.superseded_by:
            b.edge("superseded_by", version_node_id(v.id),
                   version_node_id(v.superseded_by), status[v.superseded_by])
        for ref in v.maps_to:
            node = "option:" + ref
            if node in option_ids:
                b.edge("maps_to", version_node_id(v.id), node)
            else:
                b.warnings.append("version %s maps_to unknown option %s"
                                  % (v.id, ref))


def add_lineage(b: Any, lineage: Lineage) -> None:
    """Version nodes and edges; marks catalogue-rejected options."""
    eras = sorted({v.era for v in lineage.versions})
    for v in lineage.versions:
        b.node(_version_node(v, eras.index(v.era)))
    option_ids = {n["id"] for n in b.nodes if n["type"] == "option"}
    _add_edges(b, lineage, option_ids)
    rejected = {"option:%s.%s" % (o.fork, o.id) for o in lineage.options
                if o.status == "rejected"}
    for node in b.nodes:
        if node["id"] in rejected:
            node["status"] = "rejected"
            node["attrs"]["catalogue_status"] = "rejected"
