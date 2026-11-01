/**
 * pm-eml-diagram.js - generic collapsible SVG renderer for compact operator trees.
 *
 * Tree form: leaf = [label, kind]; internal = [label, kind, child, child, ...].
 * No project-specific code: a candidate to move into eml_math.web.
 *
 *   PMEmlDiagram.render(container, tree, {
 *       subtrees:  { leafLabel: tree },   // optional trees attached under a leaf
 *       collapsed: false,                 // start with every inner node collapsed
 *       ariaLabel: 'Operator tree'
 *   })  ->  { svg, nodeCount }
 *
 * Nodes with children are toggles (click, Enter or Space). An attached
 * subtree starts collapsed. Layout runs left to right.
 */
(function (global) {
    'use strict';

    var NS = 'http://www.w3.org/2000/svg';
    var COL = 120, ROW = 34, PAD = 16, R = 13;
    var OP_SYMBOL = { mul: '×', add: '+', sub: '−', div: '÷', pow: '^',
                      sqrt: '√', neg: '−', inv: '1/·', exp: 'exp', log: 'ln' };
    var LEAF_KINDS = { v: 1, '#': 1, C: 1, P: 1, _: 1, '?': 1 };

    /** Display text for an operator label. */
    function opText(label) { return OP_SYMBOL[label] || label; }

    /** Build a layout node from a compact array; attached subtrees start collapsed. */
    function build(arr, subtrees, path, state) {
        var node = { label: String(arr[0]), kind: arr[1], id: path, kids: [] };
        for (var i = 2; i < arr.length; i++) {
            node.kids.push(build(arr[i], subtrees, path + '.' + (i - 2), state));
        }
        if (!node.kids.length && subtrees && subtrees[node.label]) {
            node.kids.push(build(subtrees[node.label], null, path + '.s', state));
            state[path] = true;
        }
        return node;
    }

    /** Assign x (depth) and y (row) to visible nodes; returns the next free row. */
    function layout(node, depth, row, state, out) {
        node.x = depth;
        if (!node.kids.length || state[node.id]) { node.y = row; out.push(node); return row + 1; }
        var ys = [];
        node.kids.forEach(function (k) { row = layout(k, depth + 1, row, state, out); ys.push(k.y); });
        node.y = (ys[0] + ys[ys.length - 1]) / 2;
        out.push(node);
        return row;
    }

    /** Create an SVG element with attributes and optional text. */
    function el(name, attrs, text) {
        var e = document.createElementNS(NS, name);
        Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
        if (text !== undefined) e.textContent = text;
        return e;
    }

    /** Leaf text with the part after the first underscore set as a subscript. */
    function leafText(label) {
        var t = el('text', { x: -R + 2, 'dominant-baseline': 'central', 'font-size': 13 });
        var i = label.indexOf('_');
        if (i <= 0) { t.textContent = label; return t; }
        t.appendChild(document.createTextNode(label.slice(0, i)));
        t.appendChild(el('tspan', { 'font-size': 10, dy: 4 }, label.slice(i + 1).replace(/_/g, ' ')));
        return t;
    }

    /** Make a group keyboard-operable as a toggle button. */
    function makeToggle(grp, node, collapsed, flip) {
        grp.setAttribute('role', 'button');
        grp.setAttribute('tabindex', '0');
        grp.setAttribute('data-node', node.id);
        grp.setAttribute('aria-expanded', String(!collapsed));
        grp.setAttribute('aria-label', (collapsed ? 'Expand ' : 'Collapse ') + opText(node.label) + ' subtree');
        grp.style.cursor = 'pointer';
        grp.addEventListener('click', flip);
        grp.addEventListener('keydown', function (ev) {
            if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); flip(); }
        });
    }

    /** Draw one node; nodes with children become toggles. */
    function drawNode(g, node, state, redraw) {
        var cx = PAD + node.x * COL + R, cy = PAD + node.y * ROW + R;
        var grp = el('g', { transform: 'translate(' + cx + ',' + cy + ')' });
        if (node.kids.length || !LEAF_KINDS[node.kind]) {
            grp.appendChild(el('circle', { r: R, fill: 'none', stroke: 'currentColor', 'stroke-width': 1.5 }));
            grp.appendChild(el('text', { 'text-anchor': 'middle', 'dominant-baseline': 'central',
                                         'font-size': 13, 'font-weight': 600 }, opText(node.label)));
        } else {
            grp.appendChild(leafText(node.label));
        }
        if (node.kids.length) {
            var collapsed = !!state[node.id];
            if (collapsed) grp.appendChild(el('text', { x: R + 4, 'font-size': 11, 'dominant-baseline': 'central' }, '[+]'));
            makeToggle(grp, node, collapsed, function () { state[node.id] = !state[node.id]; redraw(node.id); });
        }
        g.appendChild(grp);
    }

    /** Draw elbow edges from each expanded parent to its children. */
    function drawEdges(g, nodes, state) {
        nodes.forEach(function (n) {
            if (!n.kids.length || state[n.id]) return;
            n.kids.forEach(function (k) {
                var x1 = PAD + n.x * COL + 2 * R, y1 = PAD + n.y * ROW + R;
                var x2 = PAD + k.x * COL, y2 = PAD + k.y * ROW + R, mx = (x1 + x2) / 2;
                g.appendChild(el('path', { d: 'M' + x1 + ',' + y1 + ' H' + mx + ' V' + y2 + ' H' + x2,
                                           fill: 'none', stroke: 'currentColor', 'stroke-opacity': 0.4 }));
            });
        });
    }

    /** Mark every inner node below the root collapsed. */
    function collapseAll(node, state) {
        node.kids.forEach(function (k) { if (k.kids.length) state[k.id] = true; collapseAll(k, state); });
    }

    /** Render the tree into container; returns the controller {svg, nodeCount}. */
    function render(container, tree, opts) {
        opts = opts || {};
        var state = {};
        var root = build(tree, opts.subtrees || null, 'r', state);
        if (opts.collapsed) collapseAll(root, state);
        var ctl = { svg: null, nodeCount: 0 };

        function redraw(focusId) {
            var nodes = [], rows = layout(root, 0, 0, state, nodes);
            var maxX = Math.max.apply(null, nodes.map(function (n) { return n.x; }));
            var w = PAD * 2 + (maxX + 1) * COL + 40, h = PAD * 2 + rows * ROW;
            var svg = el('svg', { width: w, height: h, viewBox: '0 0 ' + w + ' ' + h, role: 'group',
                                  'aria-label': opts.ariaLabel || 'Operator tree', 'class': 'pm-eml-diagram',
                                  style: 'color:var(--text-primary,#222);font-family:inherit;fill:currentColor' });
            var g = el('g', {}); svg.appendChild(g);
            drawEdges(g, nodes, state);
            nodes.forEach(function (n) { drawNode(g, n, state, redraw); });
            container.replaceChildren(svg);
            ctl.svg = svg; ctl.nodeCount = nodes.length;
            if (focusId) {
                var again = svg.querySelector('[data-node="' + focusId + '"]');
                if (again) again.focus();
            }
        }
        redraw();
        return ctl;
    }

    global.PMEmlDiagram = { render: render };
})(window);
