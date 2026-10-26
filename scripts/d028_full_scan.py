"""Full D-028 scan on the Rust core: analyse every symmetry class of the
D-028 class and write one JSON record per class (resumable).

Usage (from the repo root, PYTHONPATH=src, with the built extension in
src/metaphysica/_physica_core*.pyd):

    python scripts/d028_full_scan.py OUT.jsonl [--max-order 1536]
        [--procs 16] [--delta-orders 3 4] [--classes CLASSES.pkl]

The class enumeration (`scan_classes`) is deterministic; `--classes` reuses a
pickle written by this script for the same `--max-order`, so a rerun skips
the slow enumeration. Classes already present in OUT.jsonl are skipped.
Nothing here changes the D-028 class definition or any ruling.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import pickle
import time


from metaphysica.simulations.PM.geometry import orbifold_gauge_scan as o


def _pack(c):
    return (c["lat"].name, c["lat"].L, [(g.M, g.c) for g in c["G"]],
            c["family"], c["delta_order"], c["candidates"])


def _unpack(p):
    name, L, mats, fam, dord, cand = p
    return {"lat": o.Lattice(name, L), "G": [o.Iso(M, c) for M, c in mats],
            "family": fam, "delta_order": dord, "candidates": cand}


def _enumerate(max_order: int, pkl: str):
    if pkl and os.path.exists(pkl):
        with open(pkl, "rb") as fh:
            return pickle.load(fh)
    classes, tally = o.scan_classes(max_order=max_order)
    packed = ([_pack(c) for c in classes], tally)
    if pkl:
        with open(pkl, "wb") as fh:
            pickle.dump(packed, fh)
    return packed


def _job(arg):
    idx, packed = arg
    c = _unpack(packed)
    t = time.time()
    try:
        rec = o.analyse(c["G"], c["lat"], backend="rust", threads=1)
        rec["error"] = None
    except o.ScanError as exc:  # recorded, never guessed
        rec = {"order": len(c["G"]), "error": str(exc)}
    rec.update({"class": idx, "family": c["family"], "lattice": c["lat"].name,
                "delta_order": c["delta_order"], "candidates": c["candidates"],
                "seconds": round(time.time() - t, 2)})
    return rec


def _done(path: str) -> set:
    if not os.path.exists(path):
        return set()
    with open(path) as fh:
        return {json.loads(line)["class"] for line in fh if line.strip()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--max-order", type=int, default=o.MAX_ORDER)
    ap.add_argument("--procs", type=int, default=16)
    ap.add_argument("--delta-orders", type=int, nargs="*", default=[3, 4])
    ap.add_argument("--classes", default="")
    a = ap.parse_args()
    packed, tally = _enumerate(a.max_order, a.classes)
    print("classes", len(packed), "tally", {k: v for k, v in tally.items()
                                            if k != "rejected"},
          "rejected", tally["rejected"], flush=True)
    skip = _done(a.out)
    todo = [(i, p) for i, p in enumerate(packed)
            if p[4] in a.delta_orders and i not in skip]
    todo.sort(key=lambda ip: -len(ip[1][2]))  # largest groups first
    print("to analyse", len(todo), "already", len(skip), flush=True)
    t0 = time.time()
    with mp.Pool(a.procs) as pool, open(a.out, "a") as out:
        for n, rec in enumerate(pool.imap_unordered(_job, todo, chunksize=1)):
            out.write(json.dumps(rec, default=int) + "\n")
            out.flush()
            print("%d/%d class %d order %s %.1fs (elapsed %.0fs)" % (
                n + 1, len(todo), rec["class"], rec["order"], rec["seconds"],
                time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
