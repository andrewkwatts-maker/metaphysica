"""The certificate's bibliography: one record per source, cited by key.

Every entry was checked against the source before it was used (2026-09-30):
the arXiv texts of Lukas-Morris, Acharya-Denef-Valandro and Acharya were read
and the equations used are quoted in the site repo's docs/DECISION_LOG.md
(D-005); the Armstrong citation was confirmed against its indexed record
(MR0221488, DOI 10.1017/S0305004100042845); the two Joyce records reuse the fields already carried by
g2_geometry. Bonan, Eguchi-Hanson and Wang were checked against their indexed
records on 2026-10-25 (Bonan has no DOI). No DOI or URL is given unless it was verified.

A formula's `derivation.references` and the simulation's get_references()
both render from here, so a citation cannot be corrected in one place and
left stale in the other.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

__all__ = [
    "REFERENCES",
    "REF_JOYCE_1996",
    "REF_JOYCE_1996_II",
    "REF_JOYCE_2000",
    "REF_ARMSTRONG",
    "REF_ACHARYA_1999",
    "REF_LUKAS_MORRIS",
    "REF_ADV_2005",
    "REF_ACHARYA_1996",
    "REF_BRYANT_1987",
    "REF_EGUCHI_HANSON_1978",
    "REF_WANG_1989",
    "cite",
    "short_cite",
    "reference_records",
]

REF_JOYCE_1996 = "joyce1996"
REF_JOYCE_1996_II = "joyce1996ii"
REF_JOYCE_2000 = "joyce2000"
REF_ARMSTRONG = "armstrong1968"
REF_ACHARYA_1999 = "acharya1999"
REF_LUKAS_MORRIS = "lukas_morris2004"
REF_ADV_2005 = "acharya_denef_valandro2005"
REF_ACHARYA_1996 = "acharya1996"
REF_BRYANT_1987 = "bryant-1987"  # the id the appendices already use
REF_EGUCHI_HANSON_1978 = "eguchi_hanson1978"
REF_WANG_1989 = "wang1989"

REFERENCES: Dict[str, Dict[str, Any]] = {
    REF_BRYANT_1987: {
        "authors": "Bryant, R. L.",
        "title": "Metrics with exceptional holonomy",
        "journal": "Ann. of Math. (2)",
        "volume": "126",
        "issue": "3",
        "year": 1987,
        "doi": "10.2307/1971360",
        "url": "https://annals.math.princeton.edu/1987/126-3/p06",
        "type": "article",
        "relevance": ("a torsion-free G2 structure has a Ricci-flat metric "
                      "(first observed by Bonan, C. R. Acad. Sci. Paris 262, "
                      "1966, which has no DOI or online copy)"),
    },
    REF_EGUCHI_HANSON_1978: {
        "authors": "Eguchi, T., Hanson, A. J.",
        "title": "Asymptotically flat self-dual solutions to Euclidean gravity",
        "journal": "Phys. Lett. B",
        "volume": "74",
        "pages": "249-251",
        "year": 1978,
        "type": "article",
        "doi": "10.1016/0370-2693(78)90566-X",
        "url": "https://doi.org/10.1016/0370-2693(78)90566-X",
        "relevance": (
            "the hyperkahler ALE metric that resolves each C^2/Z2 singularity"),
    },
    REF_WANG_1989: {
        "authors": "Wang, M. Y.",
        "title": "Parallel spinors and parallel forms",
        "journal": "Ann. Global Anal. Geom.",
        "volume": "7",
        "pages": "59-68",
        "year": 1989,
        "type": "article",
        "doi": "10.1007/BF00137402",
        "url": "https://doi.org/10.1007/BF00137402",
        "relevance": (
            "a parallel spinor exists only for holonomy SU(m), Sp(m), G2 or "
            "Spin(7); the count of invariant spinors (H7)"),
    },
    REF_JOYCE_1996: {
        "authors": "Joyce, D. D.",
        "title": "Compact Riemannian 7-manifolds with holonomy G2. I",
        "journal": "J. Differential Geom.",
        "volume": "43",
        "pages": "291-328",
        "year": 1996,
        "type": "article",
        "url": "https://projecteuclid.org/euclid.jdg/1214458109",
        "relevance": (
            "The construction: resolving T^7/Gamma with Eguchi-Hanson spaces; "
            "the (Z/2)^3 example with b_2 = 12, b_3 = 43"),
    },
    REF_JOYCE_1996_II: {
        "authors": "Joyce, D. D.",
        "title": "Compact Riemannian 7-manifolds with holonomy G2. II",
        "journal": "J. Differential Geom.",
        "volume": "43",
        "pages": "329-375",
        "year": 1996,
        "type": "article",
        "doi": "10.4310/jdg/1214458110",
        "url": "https://projecteuclid.org/euclid.jdg/1214458110",
        "relevance": (
            "Resolutions with a free extra stabiliser (Theorems 2.2.2-2.2.3); "
            "Example 4, b_2 = 8 + l, b_3 = 47 - l; Proposition 1.1.1, "
            "holonomy G2 iff pi_1 finite"),
    },
    REF_JOYCE_2000: {
        "authors": "Joyce, D. D.",
        "title": "Compact Manifolds with Special Holonomy",
        "publisher": "Oxford University Press",
        "year": 2000,
        "type": "book",
        "doi": "10.1093/oso/9780198506010.001.0001",
        "url": "https://doi.org/10.1093/oso/9780198506010.001.0001",
        "relevance": (
            "Compact G2-manifolds from resolutions of T^7/Gamma, and the "
            "cohomology of the resolution; Theorem 11.6.1, the existence of a "
            "torsion-free G2 structure near a closed one of small torsion"),
    },
    REF_ARMSTRONG: {
        "authors": "Armstrong, M. A.",
        "title": ("The fundamental group of the orbit space of a discontinuous "
                  "group"),
        "journal": "Proc. Cambridge Philos. Soc.",
        "volume": "64",
        "pages": "299-301",
        "year": 1968,
        "type": "article",
        "doi": "10.1017/S0305004100042845",
        "url": "https://doi.org/10.1017/S0305004100042845",
        "relevance": (
            "pi_1 of a quotient is the group modulo the subgroup generated by "
            "elements with fixed points"),
    },
    REF_ACHARYA_1999: {
        "authors": "Acharya, B. S.",
        "title": "M theory, Joyce orbifolds and super Yang-Mills",
        "journal": "Adv. Theor. Math. Phys.",
        "volume": "3",
        "pages": "227-248",
        "year": 1999,
        "type": "article",
        "arxiv": "hep-th/9812205",
        "url": "https://arxiv.org/abs/hep-th/9812205",
        "relevance": (
            "The local gauge theory on C^2/Gamma fibred over a 3-manifold M: "
            "pure N = (1 + b_1(M)) super Yang-Mills; N = 4 when M = T^3"),
    },
    REF_ACHARYA_1996: {
        "authors": "Acharya, B. S.",
        "title": "N=1 heterotic/M theory duality and Joyce manifolds",
        "journal": "Nucl. Phys. B",
        "volume": "475",
        "pages": "579-596",
        "year": 1996,
        "type": "article",
        "arxiv": "hep-th/9603033",
        "url": "https://arxiv.org/abs/hep-th/9603033",
        "relevance": (
            "M-theory on Joyce manifolds (as K3 fibrations) dual to heterotic "
            "strings on T^3-fibred Calabi-Yau threefolds; massless spectra "
            "agree"),
    },
    REF_LUKAS_MORRIS: {
        "authors": "Lukas, A., Morris, S.",
        "title": "Moduli Kahler potential for M-theory on a G2 manifold",
        "journal": "Phys. Rev. D",
        "volume": "69",
        "pages": "066003",
        "year": 2004,
        "type": "article",
        "arxiv": "hep-th/0305078",
        "url": "https://arxiv.org/abs/hep-th/0305078",
        "relevance": (
            "The moduli Kahler potential (eq. 5.10, Table 1) for exactly "
            "Joyce's T^7/Z_2^3: 7 bulk and 36 blow-up moduli"),
    },
    REF_ADV_2005: {
        "authors": "Acharya, B. S., Denef, F., Valandro, R.",
        "title": "Statistics of M theory vacua",
        "journal": "JHEP",
        "volume": "0506",
        "pages": "056",
        "year": 2005,
        "type": "article",
        "arxiv": "hep-th/0502060",
        "url": "https://arxiv.org/abs/hep-th/0502060",
        "relevance": (
            "The G4 flux superpotential with its Chern-Simons constant, and "
            "the potential on the axion slice (eqs. 3.4, 3.11, 3.18)"),
    },
}


def cite(key: str) -> str:
    """One line: Authors (year) 'Title', Journal volume, pages[, arXiv]."""
    ref = REFERENCES[key]
    venue = ref.get("journal") or ref.get("publisher", "")
    detail = " ".join(p for p in (ref.get("volume"), ref.get("pages")) if p)
    text = "%s (%d) '%s', %s" % (ref["authors"], ref["year"], ref["title"],
                                 venue)
    if detail:
        text += " " + detail
    if ref.get("arxiv"):
        text += ", " + ref["arxiv"]
    return text


def short_cite(key: str) -> str:
    """Author-year form for running text: 'Joyce 1996a', 'Lukas & Morris 2004'.

    Surnames are the even tokens of the 'Surname, Initials, Surname, ...'
    authors field. Two records sharing surnames and year get a, b, ... in
    key order, so the two Joyce 1996 papers stay distinguishable.
    """
    def base(k: str) -> str:
        ref = REFERENCES[k]
        names = [t.strip() for t in ref["authors"].split(",")][0::2]
        if len(names) == 1:
            who = names[0]
        elif len(names) == 2:
            who = "%s & %s" % (names[0], names[1])
        else:
            who = "%s et al." % names[0]
        return "%s %d" % (who, ref["year"])

    mine = base(key)
    twins = sorted(k for k in REFERENCES if base(k) == mine)
    if len(twins) > 1:
        mine += "abcdefghij"[twins.index(key)]
    return mine


def reference_records(keys: Sequence[str]) -> List[Dict[str, Any]]:
    """get_references() records for `keys`, first occurrence order."""
    out, seen = [], set()
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(REFERENCES[key], key=key, id=key))
    return out
