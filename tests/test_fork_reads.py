"""The read tracker: counters, the closed-gate counter, the atexit file."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from metaphysica.simulations.core import variants as V


def test_resolve_counts_reads_and_reset_clears():
    V.reset_reads()
    V.resolve("dark_energy_mechanism")
    V.resolve("dark_energy_mechanism")
    assert V.reads() == {"dark_energy_mechanism": 2}
    V.reset_reads()
    assert V.reads() == {} and V.closed_gate_reads() == {}


def test_inspection_helpers_do_not_count():
    V.reset_reads()
    V.active_selection()
    V.describe()
    V.off_table_selections()
    assert V.reads() == {} and V.closed_gate_reads() == {}


def test_read_of_a_closed_gate_fork_goes_to_the_closed_counter():
    V.reset_reads()
    with V.forced({"dark_energy_mechanism": "mep_11_13"}):
        V.resolve("dark_energy_betti")
    assert V.reads().get("dark_energy_betti") is None
    assert V.closed_gate_reads() == {"dark_energy_betti": 1}
    V.reset_reads()
    V.resolve("dark_energy_betti")          # default: thawing_quintessence
    assert V.reads() == {"dark_energy_betti": 1}
    assert V.closed_gate_reads() == {}


def test_a_subprocess_writes_its_reads_at_exit(tmp_path):
    env = dict(os.environ, METAPHYSICA_FORK_READS_DIR=str(tmp_path))
    code = ("from metaphysica.simulations.core.variants import resolve;"
            "resolve('dark_energy_mechanism')")
    proc = subprocess.run([sys.executable, "-c", code], env=env, check=True)
    assert proc.returncode == 0
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    # Import-time consumers (b3_seed) read too; the mechanism read is ours.
    assert data["reads"]["dark_energy_mechanism"] == 1
    assert data["closed_gate_reads"] == {}
