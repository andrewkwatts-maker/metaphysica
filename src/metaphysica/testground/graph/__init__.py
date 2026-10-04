"""Path graph: every fork, option, constraint and decision as one drawable graph.

`rationale` splits a fork's prose into labelled sections, `build` assembles the
graph (nodes, edges, configurations, the active path), `layout` places it in
integer coordinates computed here so the website and the app draw identical
positions, and `export` validates and writes `path_graph.json` (plus an
optional standalone HTML viewer).

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
