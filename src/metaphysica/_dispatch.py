#====== metaphysica/src/metaphysica/_dispatch.py ======#
#!copyright (c) 2025 Andrew Keith Watts. All rights reserved.
#!
#!This is the intellectual property of Andrew Keith Watts. Unauthorized
#!reproduction, distribution, or modification of this code, in whole or in part,
#!without the express written permission of Andrew Keith Watts is strictly prohibited.
#!
#!For inquiries, please contact AndrewKWatts@Gmail.com

# Rust impl: rust/physica_core/src/pyfacade.rs
"""Dispatch helpers: route public API functions to the Rust backend when available.

The Rust core (``metaphysica._physica_core``, built from ``rust/physica_core``
by maturin) is optional. When it is absent the pure-Python path runs, so
importing this package is always safe.

WHY THE IMPORT FAILURE IS RECORDED RATHER THAN DISCARDED
--------------------------------------------------------
This module used to be::

    try:
        import metaphysica._physica_core as _native
        _HAS_RUST = True
    except ImportError:
        pass

which collapses four distinct situations -- extension not built, extension
built for another Python ABI, extension present but failing to load its DLLs,
extension importable but stale -- into one silent ``False``. A user then has
no way to tell "I am running the Python path on purpose" from "the accelerated
path I paid for is broken". The import result is now kept, and
:func:`backend_report` and :func:`assert_rust_backend` expose it. Those two
functions are named in ``pyproject.toml``'s ``[rust]`` extra as the promise
that the fallback is *not* silent; until now neither existed.

``ImportError`` alone is also too narrow on Windows, where a missing MSVC
runtime surfaces as ``OSError``. The catch is broad, but nothing is swallowed:
the exception is stored and reported verbatim.
"""
from __future__ import annotations

import functools
from typing import Any, Callable, Optional

#: The imported extension module, or ``None``.
_native: Any = None
#: ``True`` only when the extension imported successfully.
_HAS_RUST: bool = False
#: The exception that stopped the extension importing, or ``None``.
_IMPORT_ERROR: Optional[BaseException] = None
#: Rust symbols a caller looked for and did not find, in lookup order.
_MISSING_SYMBOLS: list = []

try:
    import metaphysica._physica_core as _native  # type: ignore[import-not-found]
    _HAS_RUST = True
except Exception as exc:  # noqa: BLE001 - deliberately broad, and recorded below
    _IMPORT_ERROR = exc


def rust_fn(name: str) -> Optional[Callable[..., Any]]:
    """Return the Rust function *name*, or ``None`` when it is unavailable.

    A missing symbol is recorded in :data:`_MISSING_SYMBOLS` so
    :func:`backend_report` can name it. That distinction matters: a symbol the
    extension does not export is a build/version mismatch, which looks
    identical to "no extension" unless someone writes it down.
    """
    if not _HAS_RUST or _native is None:
        return None
    fn = getattr(_native, name, None)
    if fn is None and name not in _MISSING_SYMBOLS:
        _MISSING_SYMBOLS.append(name)
    return fn


def backend_report() -> dict:
    """Describe the state of the Rust backend.

    Keys:
        ``available``      -- did the extension import
        ``import_error``   -- the failure text, or ``None``
        ``rust_version``   -- ``_physica_core.__version__``, or ``None``
        ``python_version`` -- ``metaphysica.__version__``
        ``version_match``  -- do the two agree
        ``missing_symbols``-- Rust names looked up and not found so far
        ``exports``        -- public names the extension provides
    """
    from metaphysica import __version__ as py_version

    rust_version = getattr(_native, "__version__", None) if _HAS_RUST else None
    exports = (
        sorted(n for n in dir(_native) if not n.startswith("__"))
        if _HAS_RUST and _native is not None
        else []
    )
    return {
        "available": _HAS_RUST,
        "import_error": None if _IMPORT_ERROR is None else f"{type(_IMPORT_ERROR).__name__}: {_IMPORT_ERROR}",
        "rust_version": rust_version,
        "python_version": py_version,
        "version_match": rust_version == py_version,
        "missing_symbols": list(_MISSING_SYMBOLS),
        "exports": exports,
    }


def assert_rust_backend() -> None:
    """Raise unless the Rust backend is importable and version-matched.

    ``pyproject.toml`` advertises this call as the way to prove the
    accelerated path is live. It raises
    :class:`metaphysica.MetaphysicaBackendError` with the full
    :func:`backend_report` attached, so a CI failure says which of the four
    failure modes actually happened.
    """
    from metaphysica._errors import MetaphysicaRustBackendError

    report = backend_report()
    if not report["available"]:
        raise MetaphysicaRustBackendError(
            "the Rust backend (metaphysica._physica_core) is not available: "
            f"{report['import_error']}. Build it with "
            "`maturin develop --features extension-module`.",
            report,
        )
    if not report["version_match"]:
        raise MetaphysicaRustBackendError(
            "the Rust extension is stale: it reports version "
            f"{report['rust_version']!r} but the Python package is "
            f"{report['python_version']!r}. Rebuild with "
            "`maturin develop --features extension-module`.",
            report,
        )


def rust_accelerated(rust_fn_name: str):
    """Dispatch to a Rust backend function by name, else run the Python body.

    NOTE ON USE. This decorator hides the Python implementation behind the
    wrapper, which makes the two paths impossible to compare from a test. New
    call sites should instead keep the Python body as a named
    ``_<name>_python`` method and choose between them explicitly, as
    ``E8SpherePacking.enumerate_lattice_points`` and
    ``FlatTorusDirac.analytic_eigenvalues`` now do -- that is what lets
    ``tests/test_rust_python_parity.py`` assert the two agree numerically.
    The decorator is kept because it is part of the public surface.
    """
    def decorator(py_fn):
        @functools.wraps(py_fn)
        def wrapper(*args, **kwargs):
            fn = rust_fn(rust_fn_name)
            if fn is not None:
                return fn(*args, **kwargs)
            return py_fn(*args, **kwargs)
        return wrapper
    return decorator
