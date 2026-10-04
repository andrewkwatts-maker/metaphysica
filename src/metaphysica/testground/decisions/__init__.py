"""Decisions: read and append a theory's decision log.

`log` parses a Markdown decision log (headings ``## D-NNN · date · gate ·
STATUS — title``, several entries per id); `write` renders and appends the
entries the test ground creates (PATH ACCEPT, PATH RETIRE, PATH REINSTATE).
Appending never rewrites or removes an existing entry.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""
