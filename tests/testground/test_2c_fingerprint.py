"""Lane 2C: the engine fingerprint is stable and moves with the code.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import re

from metaphysica.testground.runner import fingerprint as fp_mod
from metaphysica.testground.runner.fingerprint import (dependency_versions,
                                                       engine_fingerprint,
                                                       fingerprint_manifest,
                                                       source_files)


def _tree(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
    return root


def test_stable_across_calls_and_root_order(tmp_path):
    a = _tree(tmp_path / "a", {"x.py": "X = 1\n", "sub/y.py": "Y = 2\n"})
    b = _tree(tmp_path / "b", {"z.py": "Z = 3\n"})
    first = engine_fingerprint([a, b])
    assert first == engine_fingerprint([b, a]) == engine_fingerprint([a, b, a])
    assert re.fullmatch(r"[0-9a-f]{16}", first)
    assert len(engine_fingerprint([a], length=64)) == 64


def test_it_moves_when_code_or_layout_changes(tmp_path):
    root = _tree(tmp_path / "src", {"x.py": "X = 1\n"})
    before = engine_fingerprint([root])
    (root / "x.py").write_text("X = 2\n", encoding="utf-8")
    edited = engine_fingerprint([root])
    (root / "x.py").rename(root / "w.py")
    renamed = engine_fingerprint([root])
    assert len({before, edited, renamed}) == 3


def test_line_endings_caches_hidden_dirs_and_non_python_do_not_count(tmp_path):
    lf = _tree(tmp_path / "lf" / "pkg", {"x.py": "X = 1\nY = 2\n"})
    crlf = _tree(tmp_path / "crlf" / "pkg", {"x.py": "X = 1\r\nY = 2\r\n"})
    assert engine_fingerprint([lf]) == engine_fingerprint([crlf])
    base = engine_fingerprint([lf])
    _tree(lf, {"__pycache__/x.py": "junk", ".hidden/h.py": "junk",
               "notes.md": "# notes", "data.json": "{}"})
    assert engine_fingerprint([lf]) == base
    assert [p.name for p in source_files(lf)] == ["x.py"]
    assert {p.name for p in source_files(lf, ("*.py", "*.json"))} == {
        "x.py", "data.json"}


def test_dependency_versions_take_part(tmp_path):
    root = _tree(tmp_path / "src", {"x.py": "X = 1\n"})
    assert dependency_versions(["no-such-dist-2c"]) == {
        "no-such-dist-2c": "absent"}
    assert dependency_versions(["PyYAML"])["PyYAML"] != "absent"
    assert engine_fingerprint([root], dependencies=["PyYAML"]) != \
        engine_fingerprint([root], dependencies=[])


def test_the_manifest_lists_what_was_hashed(tmp_path):
    root = _tree(tmp_path / "src", {"x.py": "X = 1\n"})
    manifest = fingerprint_manifest([root], dependencies=["no-such-dist-2c"])
    assert list(manifest["files"]) == ["src/x.py"]
    assert manifest["dependencies"] == {"no-such-dist-2c": "absent"}
    assert manifest["python"].startswith(fp_mod.sys.implementation.name)


def test_the_default_root_is_the_engine_package():
    roots = fp_mod.engine_roots()
    assert roots[0].name == "metaphysica"
    assert (roots[0] / "testground" / "runner" / "fingerprint.py").is_file()
    assert re.fullmatch(r"[0-9a-f]{16}", engine_fingerprint())
