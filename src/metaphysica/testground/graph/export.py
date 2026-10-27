"""Export the path graph: validate, write ``path_graph.json``, optionally HTML.

`export_graph(theory, out_path, assessment_path=None)` builds the graph,
validates it against ``testground/schemas/path_graph.schema.json`` (with
jsonschema when installed, else a structural check of the same rules) plus the
references the schema cannot express (every edge end and every layout position
names a node), and writes it with sorted keys and LF newlines, atomically. Two
exports of the same inputs are byte-identical.

With ``html`` it also writes a standalone viewer: the graph drawn as inline SVG
at the layout's positions, with a small inspector, and no external libraries.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import html as _html
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from metaphysica.testground.graph.build import (LEGEND, build_graph,
                                                load_assessment)
from metaphysica.testground.graph.ranking import load_ranking

__all__ = [
    "SCHEMA_PATH",
    "GraphInvalid",
    "load_schema",
    "validate_graph",
    "structural_errors",
    "reference_errors",
    "dumps",
    "render_html",
    "export_graph",
]

SCHEMA_PATH = (Path(__file__).resolve().parents[1] / "schemas"
               / "path_graph.schema.json")


class GraphInvalid(ValueError):
    """The graph does not satisfy the path_graph schema."""

    def __init__(self, errors: Sequence[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("path graph invalid: " + "; ".join(self.errors[:10]))


def load_schema() -> Dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


# -- validation ---------------------------------------------------------------

def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _box_errors(where: str, box: Any) -> List[str]:
    if (not isinstance(box, list) or len(box) != 4
            or not all(_is_int(v) for v in box)):
        return ["%s: expected 4 integers, got %r" % (where, box)]
    return []


def _missing(where: str, data: Any, required: Sequence[str]) -> List[str]:
    if not isinstance(data, Mapping):
        return ["%s: expected an object" % where]
    return ["%s: missing %r" % (where, k) for k in required if k not in data]


def _items_errors(graph: Mapping[str, Any], key: str,
                  item_schema: Mapping[str, Any]) -> List[str]:
    items = graph.get(key)
    if not isinstance(items, list):
        return ["%s: expected an array" % key]
    allowed = item_schema["properties"]["type"]["enum"]
    errors: List[str] = []
    for i, item in enumerate(items):
        where = "%s/%d" % (key, i)
        errors += _missing(where, item, item_schema["required"])
        if isinstance(item, Mapping) and item.get("type") not in allowed:
            errors.append("%s: type %r not in %s" % (where, item.get("type"),
                                                      allowed))
    return errors


def structural_errors(graph: Mapping[str, Any],
                      schema: Optional[Mapping[str, Any]] = None) -> List[str]:
    """The schema's rules checked by hand (used when jsonschema is absent)."""
    schema = schema or load_schema()
    props = schema["properties"]
    errors = _missing("", graph, schema["required"])
    if errors:
        return errors
    if graph["schema"] != props["schema"]["const"]:
        errors.append("schema: expected %r" % props["schema"]["const"])
    errors += _missing("theory", graph["theory"],
                       props["theory"]["required"])
    if isinstance(graph["theory"], Mapping) and "active" in graph["theory"]:
        errors += _missing("theory/active", graph["theory"]["active"],
                           ["digest"])
    errors += _items_errors(graph, "nodes", props["nodes"]["items"])
    errors += _items_errors(graph, "edges", props["edges"]["items"])
    layout = graph["layout"]
    errors += _missing("layout", layout, props["layout"]["required"])
    if not errors:
        errors += _box_errors("layout/bbox", layout["bbox"])
        for node_id, box in sorted(layout["positions"].items()):
            errors += _box_errors("layout/positions/%s" % node_id, box)
    return errors


def reference_errors(graph: Mapping[str, Any]) -> List[str]:
    """Edges and positions must name existing nodes; every node is placed."""
    ids = [n.get("id") for n in graph.get("nodes", ())]
    known = set(ids)
    errors = ["nodes: duplicate id %r" % i for i in sorted(
        {i for i in ids if ids.count(i) > 1})]
    for i, edge in enumerate(graph.get("edges", ())):
        for end in ("source", "target"):
            if edge.get(end) not in known:
                errors.append("edges/%d: %s %r is not a node"
                              % (i, end, edge.get(end)))
    layout = graph.get("layout", {})
    positions = dict(layout.get("positions", {}))
    positions.update(layout.get("lineage", {}).get("positions", {}))
    errors += ["layout: %r has no position" % i for i in sorted(
        known - set(positions))]
    errors += ["layout: position for unknown node %r" % i for i in sorted(
        set(positions) - known)]
    return errors


def validate_graph(graph: Mapping[str, Any],
                   schema: Optional[Mapping[str, Any]] = None) -> List[str]:
    """Every problem with ``graph``; an empty list means valid."""
    schema = schema or load_schema()
    try:
        import jsonschema
    except ImportError:
        errors = structural_errors(graph, schema)
    else:
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted("%s: %s" % ("/".join(str(p) for p in e.absolute_path),
                                    e.message)
                        for e in validator.iter_errors(graph))
    return errors + (reference_errors(graph) if not errors else [])


# -- writing ------------------------------------------------------------------

def dumps(graph: Mapping[str, Any]) -> str:
    """Canonical text: sorted keys, two-space indent, LF, trailing newline."""
    return json.dumps(graph, sort_keys=True, indent=2,
                      ensure_ascii=False) + "\n"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".tmp",
                               dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def export_graph(theory: Any, out_path: Union[str, Path],
                 assessment_path: Union[None, str, Path] = None,
                 html: Union[bool, str, Path] = False,
                 decision_log: Union[None, str, Path] = None,
                 ranking_path: Union[None, str, Path] = None
                 ) -> Dict[str, Any]:
    """Build, validate and write the graph; return it.

    ``html=True`` also writes ``<out_path stem>.html`` beside the JSON; a path
    writes the viewer there. Raises GraphInvalid (and writes nothing) when the
    graph does not validate.
    """
    assessment = (load_assessment(assessment_path)
                  if assessment_path is not None else None)
    ranking = (load_ranking(ranking_path)
               if ranking_path is not None else None)
    graph = build_graph(theory, assessment, decision_log, ranking)
    errors = validate_graph(graph)
    if errors:
        raise GraphInvalid(errors)
    out = Path(out_path)
    _atomic_write(out, dumps(graph))
    if html:
        target = out.with_suffix(".html") if html is True else Path(html)
        _atomic_write(target, render_html(graph))
    return graph


# -- the standalone viewer ----------------------------------------------------

_EDGE_STYLE = {
    "path_step": 'stroke-width="4" fill="none"',
    "requires": 'stroke="#4fc3f7" stroke-width="1.5" stroke-dasharray="6 4"',
    "excludes": 'stroke="#ff5c5c" stroke-width="1.5" stroke-dasharray="2 4"',
    "decided_by": 'stroke="#8a8a99" stroke-width="1" opacity="0.35"',
}


def _colour(cls: Optional[str]) -> str:
    return LEGEND.get(cls or "", {}).get("color", "#9aa4b2")


def _label(text: str, width: int) -> str:
    limit = max(4, width // 8)
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _edge_svg(edge: Mapping[str, Any], pos: Mapping[str, List[int]]) -> str:
    s, t = pos.get(edge["source"]), pos.get(edge["target"])
    if s is None or t is None or edge["type"] not in _EDGE_STYLE:
        return ""
    if edge["type"] == "path_step":
        x1, y1, x2, y2 = s[0] + s[2], s[1] + s[3] // 2, t[0], t[1] + t[3] // 2
        style = 'stroke="%s" %s' % (_colour(edge.get("class")),
                                    _EDGE_STYLE["path_step"])
    elif edge["type"] == "decided_by":
        x1, y1, x2, y2 = s[0] + s[2] // 2, s[1] + s[3], t[0] + t[2] // 2, t[1]
        style = _EDGE_STYLE["decided_by"]
    else:
        x1, y1 = s[0] + s[2] // 2, s[1] + s[3] // 2
        x2, y2 = t[0] + t[2] // 2, t[1] + t[3] // 2
        style = _EDGE_STYLE[edge["type"]]
    return ('<line class="edge %s" x1="%d" y1="%d" x2="%d" y2="%d" %s/>'
            % (_html.escape(edge["type"]), x1, y1, x2, y2, style))


def _node_svg(node: Mapping[str, Any], box: List[int]) -> str:
    x, y, w, h = box
    cls = node.get("class") or node["type"]
    fill = ('url(#hatch)' if cls == "not_implemented" else _colour(cls)
            if node["type"] == "option" else "#1e2233")
    stroke = _colour(cls) if node["type"] != "option" else "#0b0d14"
    tip = (node.get("rationale") or {}).get("summary") or (
        node.get("attrs") or {}).get("title") or ""
    text_fill = "#0b0d14" if node["type"] == "option" else "#e8eaf2"
    return ('<g class="node %s %s" data-id="%s" tabindex="0">'
            '<title>%s</title>'
            '<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" '
            'stroke="%s" stroke-width="2"/>'
            '<text x="%d" y="%d" fill="%s">%s</text></g>'
            % (_html.escape(node["type"]), _html.escape(cls),
               _html.escape(node["id"]), _html.escape(str(tip)),
               x, y, w, h, fill, stroke, x + 8, y + h // 2 + 5, text_fill,
               _html.escape(_label(str(node["label"]), w))))


def _svg(graph: Mapping[str, Any]) -> str:
    pos = graph["layout"]["positions"]
    _, _, width, height = graph["layout"]["bbox"]
    edges = [_edge_svg(e, pos) for e in graph["edges"]]
    nodes = [_node_svg(n, pos[n["id"]]) for n in graph["nodes"]
             if n["id"] in pos]
    return ('<svg id="canvas" xmlns="http://www.w3.org/2000/svg" '
            'viewBox="0 0 %d %d" role="img" aria-label="path graph">'
            '<defs><pattern id="hatch" width="8" height="8" '
            'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="8" height="8" fill="%s"/>'
            '<line x1="0" y1="0" x2="0" y2="8" stroke="#0b0d14" '
            'stroke-width="3"/></pattern></defs>\n<g class="edges">%s</g>\n'
            '<g class="nodes">%s</g></svg>'
            % (width, height, _colour("not_implemented"),
               "".join(e for e in edges if e), "\n".join(nodes)))


_CSS = """
body{margin:0;font:14px/1.4 system-ui,sans-serif;background:#0b0d14;color:#e8eaf2;
display:flex;height:100vh}
main{flex:1;overflow:hidden;cursor:grab}main svg{width:100%;height:100%}
aside{width:340px;max-width:40vw;overflow:auto;padding:12px 16px;
border-left:1px solid #2a2f45;background:#12151f}
h1{font-size:16px;margin:0 0 4px}h2{font-size:14px;margin:12px 0 4px}
.node{cursor:pointer}.node text{font-size:12px;pointer-events:none}
.legend span{display:inline-block;width:10px;height:10px;margin-right:6px}
.muted{color:#9aa4b2}pre{white-space:pre-wrap;font-size:12px}
@media (max-width:700px){body{flex-direction:column}aside{width:auto;
max-width:none;height:40vh;border-left:0;border-top:1px solid #2a2f45}}
"""

_JS = """
(function(){
var data=JSON.parse(document.getElementById('path-graph-data').textContent);
var byId={};data.nodes.forEach(function(n){byId[n.id]=n;});
var svg=document.getElementById('canvas');var box=data.layout.bbox.slice();
var view=[box[0],box[1],box[2],box[3]];
function apply(){svg.setAttribute('viewBox',view.join(' '));}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){
return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function show(id){var n=byId[id];if(!n)return;var r=n.rationale||{};
var h='<h1>'+esc(n.label)+'</h1><div class="muted">'+esc(n.type)+' · '+
esc(n.status)+' · '+esc(n['class'])+'</div>';
if(r.summary)h+='<p>'+esc(r.summary)+'</p>';
(r.sections||[]).forEach(function(s){h+='<h2>'+esc(s.heading||s.key)+
'</h2><p>'+esc(s.body)+'</p>';});
h+='<h2>attributes</h2><pre>'+esc(JSON.stringify(n.attrs||{},null,1))+'</pre>';
if(n.stats)h+='<h2>assessment</h2><pre>'+esc(JSON.stringify(n.stats,null,1))+
'</pre>';document.getElementById('inspector').innerHTML=h;
location.hash='node='+encodeURIComponent(id);}
svg.addEventListener('click',function(e){var g=e.target.closest('.node');
if(g)show(g.getAttribute('data-id'));});
svg.addEventListener('keydown',function(e){var g=e.target.closest('.node');
if(g&&(e.key==='Enter'||e.key===' '))show(g.getAttribute('data-id'));});
svg.addEventListener('wheel',function(e){e.preventDefault();
var f=e.deltaY>0?1.15:1/1.15;var cx=view[0]+view[2]/2,cy=view[1]+view[3]/2;
view[2]*=f;view[3]*=f;view[0]=cx-view[2]/2;view[1]=cy-view[3]/2;apply();},
{passive:false});
var drag=null;svg.addEventListener('mousedown',function(e){drag=[e.clientX,
e.clientY];});window.addEventListener('mouseup',function(){drag=null;});
window.addEventListener('mousemove',function(e){if(!drag)return;
var k=view[2]/svg.clientWidth;view[0]-=(e.clientX-drag[0])*k;
view[1]-=(e.clientY-drag[1])*k;drag=[e.clientX,e.clientY];apply();});
var m=/node=([^&]+)/.exec(location.hash);if(m)show(decodeURIComponent(m[1]));
})();
"""


def _legend_html() -> str:
    rows = ['<div><span style="background:%s"></span>%s: %s</div>'
            % (v["color"], _html.escape(k), _html.escape(v["label"]))
            for k, v in sorted(LEGEND.items())]
    return '<div class="legend">%s</div>' % "".join(rows)


def render_html(graph: Mapping[str, Any]) -> str:
    """A standalone HTML page drawing ``graph`` (no external resources)."""
    theory = graph["theory"]
    active = theory.get("active", {})
    payload = dumps(graph).replace("</", "<\\/")
    title = "%s — paths" % theory.get("title", theory.get("id", ""))
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, "
            "initial-scale=1\"><title>%s</title><style>%s</style></head>\n"
            "<body><main>%s</main>\n<aside id=\"inspector\"><h1>%s</h1>"
            "<p class=\"muted\">active path %s (digest %s). Click a node.</p>"
            "%s</aside>\n<script type=\"application/json\" "
            "id=\"path-graph-data\">%s</script>\n<script>%s</script>"
            "</body></html>\n"
            % (_html.escape(title), _CSS, _svg(graph),
               _html.escape(str(theory.get("title", ""))),
               _html.escape(str(active.get("name") or "")),
               _html.escape(str(active.get("digest", ""))), _legend_html(),
               payload, _JS))
