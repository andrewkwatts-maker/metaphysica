"""Resolution: which option of a fork is in force, and where that came from.

One precedence order, for every theory and every caller:

    1. an explicit ``override`` argument
    2. the per-fork environment variable ``theory.env_var(fork)``
       (e.g. ``METAPHYSICA_VARIANT_B3_SEED=seed_24``)
    3. ``METAPHYSICA_CONFIG=<name|digest>`` -- a configuration from the
       selection store, matched by name first, then by digest ("active" and
       the active configuration's own name and digest are matched too)
    4. the store's active selection

An empty string at levels 1-3 counts as unset. A selection that predates a fork
is extended with the fork's ``legacy_option`` (the behaviour from before the
fork existed), else the fork's declared default. Nothing here falls back
silently: an unknown fork is a KeyError, and an option the fork does not
declare, or a ``METAPHYSICA_CONFIG`` that matches nothing, is a
`ResolutionError`. A DISABLED option resolves like any other -- refuted is not
broken, and a refutation nobody can re-run is folklore.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import (TYPE_CHECKING, Callable, Dict, Mapping, Optional)

from metaphysica.testground.configurations.model import Configuration
from metaphysica.testground.switches.model import Fork

if TYPE_CHECKING:  # pragma: no cover - typing only
    from metaphysica.testground.theory import Theory

__all__ = [
    "CONFIG_ENV",
    "ACTIVE_ALIAS",
    "ResolutionError",
    "Resolution",
    "extend_selection",
    "active_selection",
    "find_configuration",
    "configuration_from_env",
    "resolution",
    "resolve",
    "resolve_selection",
]

#: Environment variable naming a stored configuration by name or digest.
CONFIG_ENV = "METAPHYSICA_CONFIG"
#: The name under which the store's active configuration is always found.
ACTIVE_ALIAS = "active"


class ResolutionError(ValueError):
    """A requested option or configuration does not exist."""


@dataclass(frozen=True)
class Resolution:
    """The option in force for one fork, and the level that chose it."""

    fork: str
    option: str
    #: "override", "env:<VAR>", "config:<name>" or "active".
    source: str


def _forks(theory: "Theory") -> Mapping[str, Fork]:
    return theory.switches.forks()


def _fork(theory: "Theory", fork_id: str) -> Fork:
    forks = _forks(theory)
    if fork_id not in forks:
        raise KeyError("theory %r has no fork %r; declared: %s"
                       % (theory.id, fork_id, sorted(forks)))
    return forks[fork_id]


def _fallback_option(fork: Fork) -> str:
    """Option for a fork a stored selection does not mention."""
    return fork.legacy_option or fork.default()


def extend_selection(forks: Mapping[str, Fork], selection: Mapping[str, str],
                     fallback: Optional[Callable[[Fork], str]] = None,
                     ) -> Dict[str, str]:
    """``selection`` over every declared fork, in declaration order.

    Forks the selection does not mention take ``fallback(fork)`` (default:
    the legacy option, else the declared default). Entries for forks not
    declared are kept, so nothing is dropped silently.
    """
    pick = fallback or _fallback_option
    out = {fid: (selection[fid] if fid in selection else pick(fork))
           for fid, fork in forks.items()}
    for fid in selection:
        out.setdefault(fid, selection[fid])
    return out


def active_selection(theory: "Theory") -> Dict[str, str]:
    """The store's active selection, extended over every declared fork."""
    return extend_selection(_forks(theory),
                            theory.selections.active().mapping)


def find_configuration(theory: "Theory", key: str,
                       active: Optional[Configuration] = None,
                       ) -> Configuration:
    """The stored configuration named ``key``, else the one whose digest it is.

    ``active`` saves a second read of the store when the caller has it.
    """
    active = theory.selections.active() if active is None else active
    named = dict(theory.selections.named())
    if key in named:
        return named[key]
    if key == ACTIVE_ALIAS or (active.name is not None and key == active.name):
        return active
    for cfg in named.values():
        if cfg.digest == key:
            return cfg
    if active.digest == key:
        return active
    raise ResolutionError(
        "%s=%r matches no stored configuration of theory %r (names: %s)"
        % (CONFIG_ENV, key, theory.id, sorted(named) + [ACTIVE_ALIAS]))


def configuration_from_env(theory: "Theory",
                           environ: Optional[Mapping[str, str]] = None,
                           active: Optional[Configuration] = None,
                           ) -> Optional[Configuration]:
    """The configuration ``METAPHYSICA_CONFIG`` names, or None when unset."""
    env = os.environ if environ is None else environ
    key = env.get(CONFIG_ENV, "")
    return find_configuration(theory, key, active) if key else None


def _checked(theory: "Theory", fork: Fork, option: str,
             source: str) -> Resolution:
    if option not in fork.option_ids():
        raise ResolutionError(
            "fork %r of theory %r has no option %r (from %s); available: %s"
            % (fork.id, theory.id, option, source, fork.option_ids()))
    return Resolution(fork.id, option, source)


def _from_store(theory: "Theory", fork: Fork,
                named: Optional[Configuration],
                active: Mapping[str, str]) -> Resolution:
    """Levels 3 and 4: the configuration ``METAPHYSICA_CONFIG`` names, else
    the active selection (extended for a fork it predates)."""
    if named is not None and fork.id in named.mapping:
        label = named.name or named.digest
        return _checked(theory, fork, named.mapping[fork.id],
                        "config:" + label)
    option = active[fork.id] if fork.id in active else _fallback_option(fork)
    return _checked(theory, fork, option, "active")


def _from_caller(theory: "Theory", fork: Fork, override: Optional[str],
                 env: Mapping[str, str]) -> Optional[Resolution]:
    """Levels 1 and 2: the explicit override, else the per-fork variable."""
    if override:
        return _checked(theory, fork, override, "override")
    var = theory.env_var(fork.id)
    if env.get(var):
        return _checked(theory, fork, env[var], "env:" + var)
    return None


def resolution(theory: "Theory", fork_id: str,
               override: Optional[str] = None, *,
               environ: Optional[Mapping[str, str]] = None) -> Resolution:
    """The option in force for ``fork_id`` and the precedence level that set it."""
    fork = _fork(theory, fork_id)
    env = os.environ if environ is None else environ
    chosen = _from_caller(theory, fork, override, env)
    if chosen is not None:
        return chosen
    active = theory.selections.active()
    return _from_store(theory, fork,
                       configuration_from_env(theory, env, active),
                       active.mapping)


def resolve(theory: "Theory", fork_id: str, override: Optional[str] = None,
            *, environ: Optional[Mapping[str, str]] = None) -> str:
    """The option in force for ``fork_id`` (see the module docstring)."""
    return resolution(theory, fork_id, override, environ=environ).option


def resolve_selection(theory: "Theory",
                      overrides: Optional[Mapping[str, str]] = None, *,
                      environ: Optional[Mapping[str, str]] = None,
                      ) -> Dict[str, str]:
    """Every declared fork resolved, in declaration order (store read once)."""
    forks = _forks(theory)
    given = dict(overrides or {})
    unknown = sorted(set(given) - set(forks))
    if unknown:
        raise KeyError("theory %r has no forks %s" % (theory.id, unknown))
    env = os.environ if environ is None else environ
    active = theory.selections.active()
    named = configuration_from_env(theory, env, active)
    out: Dict[str, str] = {}
    for fid, fork in forks.items():
        chosen = (_from_caller(theory, fork, given.get(fid), env)
                  or _from_store(theory, fork, named, active.mapping))
        out[fid] = chosen.option
    return out
