"""Exception hierarchy for the ``metaphysica`` public API.

Every Get* lookup, every catalog probe, and every format negotiation
ultimately raises a ``MetaphysicaError`` subtype. The exceptions
double-inherit from common stdlib types (``KeyError`` / ``ValueError`` /
``RuntimeError``) so legacy callers that catch those continue to work.

The hierarchy
-------------

::

    MetaphysicaError                       (base, inherits Exception)
    +- MetaphysicaKeyError                 (name not found — inherits KeyError)
    |   +- MetaphysicaAmbiguityError       (name resolves to multiple kinds)
    +- MetaphysicaFormatError              (format not supported — inherits ValueError)
    +- MetaphysicaBackendError             (JIT generator failed — inherits RuntimeError)

Each subtype carries machine-readable attributes alongside its message so
callers can surface helpful UI without parsing strings.
"""
from __future__ import annotations

import difflib
from typing import Iterable, List, Optional, Sequence


class MetaphysicaError(Exception):
    """Base class for every error raised by the public Get/list/get API."""


class MetaphysicaKeyError(MetaphysicaError, KeyError):
    """Raised when a name does not resolve to any known entity.

    Attributes
    ----------
    name : str
        The lookup string that failed.
    suggestions : list[str]
        Up to 3 closest matches drawn from the catalog (via ``difflib``).
    kind : str | None
        If ``kind=`` was supplied to ``get()``, the kind that was probed.
    """

    def __init__(
        self,
        name: str,
        suggestions: Optional[Sequence[str]] = None,
        kind: Optional[str] = None,
    ) -> None:
        self.name = name
        self.suggestions = list(suggestions or [])
        self.kind = kind
        scope = f" of kind {kind!r}" if kind else ""
        tail = (
            f". Did you mean: {', '.join(repr(s) for s in self.suggestions)}?"
            if self.suggestions
            else ""
        )
        super().__init__(f"No metaphysica entity{scope} named {name!r}{tail}")


class MetaphysicaAmbiguityError(MetaphysicaKeyError):
    """Raised when a name resolves to multiple entity kinds.

    Pass ``kind=`` to ``get()`` to disambiguate.
    """

    def __init__(self, name: str, candidates: Sequence[tuple]) -> None:
        # candidates is a list of (kind, canonical_id) tuples.
        self.candidates = list(candidates)
        self.name = name
        self.suggestions = []
        kinds = ", ".join(sorted({k for k, _ in self.candidates}))
        # Skip the MetaphysicaKeyError init so the message stays specific
        # to ambiguity (suggestions/closest-match aren't relevant here).
        MetaphysicaError.__init__(
            self,
            f"{name!r} matches multiple entity kinds: {kinds}. "
            f"Pass kind=<one of those> to disambiguate.",
        )


class MetaphysicaFormatError(MetaphysicaError, ValueError):
    """Raised when the requested format is not valid for the resolved entity.

    Examples
    --------
    ``metaphysica.GetFloat("section-7.4")`` — sections are text, not numeric.
    ``metaphysica.GetPNG("constants.M_PLANCK")`` — parameters don't carry an
    image render.
    """

    def __init__(
        self,
        name: str,
        kind: str,
        fmt: str,
        supported: Optional[Iterable[str]] = None,
    ) -> None:
        self.name = name
        self.kind = kind
        self.fmt = fmt
        self.supported = sorted(supported) if supported else []
        tail = (
            f"; supported for {kind}: {', '.join(self.supported)}"
            if self.supported
            else ""
        )
        super().__init__(
            f"Format {fmt!r} is not supported for {kind} {name!r}{tail}"
        )


class MetaphysicaBackendError(MetaphysicaError, RuntimeError):
    """Raised when a JIT generator or external renderer failed.

    Wraps the underlying exception so callers retain the traceback.
    """

    def __init__(self, name: str, fmt: str, cause: Exception) -> None:
        self.name = name
        self.fmt = fmt
        self.cause = cause
        super().__init__(
            f"Backend renderer failed for {name!r} (fmt={fmt!r}): "
            f"{type(cause).__name__}: {cause}"
        )


def closest_matches(name: str, pool: Iterable[str], *, n: int = 3) -> List[str]:
    """Return up to *n* closest matches to *name* from *pool*.

    Thin wrapper around :func:`difflib.get_close_matches` with a uniform
    cutoff so error messages everywhere produce the same flavour of
    "did you mean" hints.
    """
    return difflib.get_close_matches(name, list(pool), n=n, cutoff=0.6)


__all__ = [
    "MetaphysicaError",
    "MetaphysicaKeyError",
    "MetaphysicaAmbiguityError",
    "MetaphysicaFormatError",
    "MetaphysicaBackendError",
    "closest_matches",
]
