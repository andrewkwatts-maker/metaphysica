"""L3b: which D-028 classes could source SU(3) x SU(2) with chiral matter.

Usage (repo root, PYTHONPATH=src, built extension in src/metaphysica):

    python scripts/d028_gauge_source.py RECORDS.jsonl CLASSES.pkl OUT.json
        [--md OUT.md] [--procs 16]

Reads the D-028 records (read-only) and the class pickle written by
d028_full_scan.py, re-derives each SU(3)xSU(2) hit that has codim-7 points
(pure Python), classifies the local model R^7/H at every codim-7 orbit and
the SU(3)-SU(2) crossings, and writes a JSON and a Markdown candidate table.

This is a NECESSARY-CONDITION filter only. A codim-7 point where an SU(3) and
an SU(2) locus meet is where bifundamental chiral matter could localise
(Acharya-Witten hep-th/0109152); this is not a chirality or generation count,
and nothing here is adopted or changes any D-028 ruling.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import pickle
from collections import Counter

from metaphysica.simulations.PM.geometry import orbifold_gauge_scan as o


def _unpack(p):
    name, L, mats = p[0], p[1], p[2]
    return o.Lattice(name, L), [o.Iso(M, c) for M, c in mats]


def _orbit_labels(elems, loci, orbs):
    """locus index -> (kind, k) of its orbit (from the pointwise stabiliser)."""
    lab = {}
    for orb in orbs:
        loc = loci[orb[0]]
        H = [h for h in elems if o.fixes_pointwise(h, loc)]
        t = o._stratum_type(loc["dim"], H)
        for i in orb:
            lab[i] = (t["kind"], t["k"])
    return lab


def _su3_su2_crossings(loci, lab, reps_idx):
    """Histogram of meet-component dimensions between SU(3) and SU(2) loci."""
    hist = Counter()
    for ia in reps_idx:
        if lab[ia] != ("A", 3):
            continue
        a = loci[ia]
        for i, b in enumerate(loci):
            if lab[i] == ("A", 2) and b["key"] != a["key"]:
                for m in o.meet(a, b):
                    hist["dim%d" % m["dim"]] += 1
    return dict(hist)


def _point_orbits(elems, lat, reps, loci, a_loci):
    pts, seen, out = {}, set(), []
    for p in o.point_loci(reps, loci):
        H = [h for h in elems if o.fixes_pointwise(h, p)]
        if o._stab_no_fixed_vector(H, lat):
            pts[p["key"]] = p
    for key, p in pts.items():
        if key in seen:
            continue
        orb = {o.image_locus(h, p)["key"] for h in elems}
        seen |= orb
        t = o.codim7_local_type(elems, p, lat, a_loci)
        t["orbit_size"] = len(orb)
        out.append(t)
    return out


def _job(arg):
    idx, packed = arg
    lat, elems = _unpack(packed)
    loci = o.unique_loci(elems)
    orbs = o.orbits_of_loci(elems, loci)
    reps = [loci[x[0]] for x in orbs]
    lab = _orbit_labels(elems, loci, orbs)
    a_loci = [(l, lab[i][1]) for i, l in enumerate(loci) if lab[i][0] == "A"]
    pts = _point_orbits(elems, lat, reps, loci, a_loci)
    return {"class": idx, "points": pts,
            "su3_su2_crossings": _su3_su2_crossings(
                loci, lab, [x[0] for x in orbs])}


def _load(records_path):
    with open(records_path) as fh:
        return [json.loads(x) for x in fh if x.strip()]


def reason_tally(recs):
    c = Counter()
    for r in recs:
        c[",".join(o.invalid_reasons(r)) or "(none)"] += 1
    return dict(c)


def _meeting(pts):
    return [p for p in pts
            if p["a_loci_through"].get(3) and p["a_loci_through"].get(2)]


def _b1s(rec, k):
    return sorted(r["b1"] for r in rec["strata"]
                  if r["kind"] == "A" and r["k"] == k)


def build_rows(hits, comp):
    rows = []
    for r in hits:
        c = comp.get(r["class"])
        meets = _meeting(c["points"]) if c else []
        b3, b2 = _b1s(r, 3), _b1s(r, 2)
        rows.append({
            "class": r["class"], "family": r["family"], "order": r["order"],
            "gauge": r["gauge"]["text"], "codim7_orbits": len(r["codim7"]),
            "su3_su2_points": len(meets),
            "su3_su2_point_orders": sorted(p["order"] for p in meets),
            "b1_su3": b3, "b1_su2": b2, "adjoint_chirals": sum(b3) + sum(b2),
            "invalid_reasons": o.invalid_reasons(r),
            "su3_su2_crossing_dims": c["su3_su2_crossings"] if c else {}})
    rows.sort(key=lambda x: (x["su3_su2_points"] == 0, x["adjoint_chirals"],
                             x["order"], x["class"]))
    return rows


def _compact(b1s):
    c = Counter(b1s)
    return " ".join("b1=%d x%d" % (k, n) for k, n in sorted(c.items())) or "-"


def write_md(path, rows, tally_all, tally_hit, n_hits, n_c7, n_meet):
    L = ["# D-028 gauge source: SU(3) x SU(2) candidates (L3b)", "",
         "Computation only. Nothing is adopted and no D-028 ruling changes.",
         "", "**Necessary-condition filter, not a chirality or generation "
         "count.** A codim-7 point where an SU(3) and an SU(2) locus meet is "
         "where bifundamental chiral matter could localise in M-theory on G2 "
         "(Acharya-Witten hep-th/0109152; Atiyah-Witten hep-th/0107177). "
         "Whether it does needs the resolved local geometry, which is not "
         "computed. Every row is `betti_valid` false (all have crossings).",
         "", "Counts: %d SU(3)xSU(2) hits; %d with codim-7 points; %d with "
         "an SU(3)-SU(2) meeting codim-7 point." % (n_hits, n_c7, n_meet), "",
         "Invalid reasons, all %d records: %s" % (
             sum(tally_all.values()), json.dumps(tally_all)),
         "", "Invalid reasons, the %d hits: %s" % (n_hits, json.dumps(tally_hit)),
         "", "Rank: SU(3)-SU(2) meeting points > 0; fewest adjoint chirals "
         "(sum of b1 over SU(3) and SU(2) loci); smallest order.", "",
         "| class | family | order | gauge | codim-7 | SU3-SU2 pts | b1 SU(3) | "
         "b1 SU(2) | adj | reasons |", "|---|---|---|---|---|---|---|---|---|---|"]
    for x in rows:
        L.append("| %d | %s | %d | %s | %d | %d | %s | %s | %d | %s |" % (
            x["class"], x["family"], x["order"], x["gauge"],
            x["codim7_orbits"], x["su3_su2_points"], _compact(x["b1_su3"]), _compact(x["b1_su2"]),
            x["adjoint_chirals"], ",".join(x["invalid_reasons"])))
    open(path, "w", encoding="utf8").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records")
    ap.add_argument("classes")
    ap.add_argument("out")
    ap.add_argument("--md", default="")
    ap.add_argument("--procs", type=int, default=16)
    a = ap.parse_args()
    recs = _load(a.records)
    hits = [r for r in recs if r.get("gauge", {}).get("has_su3_su2")]
    todo = [r for r in hits if r["codim7"]]
    packed, _ = pickle.load(open(a.classes, "rb"))
    for r in todo:
        assert len(packed[r["class"]][2]) == r["order"], r["class"]
    with mp.Pool(a.procs) as pool:
        res = pool.map(_job, [(r["class"], packed[r["class"]]) for r in todo],
                       chunksize=1)
    comp = {x["class"]: x for x in res}
    rows = build_rows(hits, comp)
    n_meet = sum(1 for x in rows if x["su3_su2_points"])
    summary = {"n_records": len(recs), "n_hits": len(hits),
               "n_codim7": len(todo), "n_su3_su2_meeting": n_meet,
               "reasons_all": reason_tally(recs),
               "reasons_hits": reason_tally(hits)}
    with open(a.out, "w") as fh:
        json.dump({"summary": summary, "rows": rows, "classes": comp}, fh,
                  indent=1, default=str)
    if a.md:
        write_md(a.md, rows, summary["reasons_all"], summary["reasons_hits"],
                 len(hits), len(todo), n_meet)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
