"""Publication: the certificate as formulas, a paper subsection, certificates,
proofs, self-validation, references and learning material.

SSOT rules 1-8 all apply, and each is met with content read from the
certificate rather than written for the rule: the section renders the live
statements, the certificates are the theorems' verdicts, and self-validation
adds the one check the theorems cannot make about themselves -- that the seed
the REGISTRY carries is the pair the construction derives. A registry that
disagreed would be running a mixed state, the defect class that once put b_2
at 12 beside b_3 at 24.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from metaphysica.simulations.base import (
    ContentBlock,
    Formula,
    Parameter,
    SectionContent,
    SimulationBase,
    SimulationMetadata,
)
from metaphysica.simulations.PM.geometry.closed_geometry.certificate import (
    THEOREMS,
    certificate,
)
from metaphysica.simulations.PM.geometry.closed_geometry.references import (
    cite,
    reference_records,
)
from metaphysica.simulations.PM.geometry.closed_geometry.theorem import (
    Theorem,
    build,
)

_SEED_INPUTS = ("topology.b2", "topology.elder_kads")

_LEARNING = (
    {
        "topic": "G2 manifolds",
        "url": "https://en.wikipedia.org/wiki/G2_manifold",
        "relevance": "Y_7 is a compact 7-manifold with a G2-structure",
        "validation_hint": (
            "Check that the certificate's Riemannian statements are scoped to "
            "the compact real form"),
    },
    {
        "topic": "Euler characteristic and Poincare duality",
        "url": "https://en.wikipedia.org/wiki/Euler_characteristic",
        "relevance": "chi(Y_7) = 0 and the duality check on the Betti numbers",
        "validation_hint": (
            "Confirm chi vanishes for every closed odd-dimensional manifold, "
            "so the content is the derived sequence, not the zero"),
    },
    {
        "topic": "Orbifolds and their fundamental group",
        "url": "https://en.wikipedia.org/wiki/Orbifold",
        "relevance": "T^7/Gamma, its singular set, and pi_1 of the quotient",
        "validation_hint": (
            "Check Armstrong's theorem is applied to the affine group, and "
            "that the surviving-coordinate witness really has infinite order"),
    },
    {
        "topic": "Lukas-Morris moduli Kahler potential",
        "url": "https://arxiv.org/abs/hep-th/0305078",
        "relevance": "the Kahler potential used for the flux runaway",
        "validation_hint": (
            "Check Table 1 is transcribed verbatim and the domain restriction "
            "(small U/T) is respected by the sampled points"),
    },
)


class ClosedGeometrySimulation(SimulationBase):
    """Publishes the certificate: one formula per derivable theorem."""

    def __init__(self) -> None:
        self._cert: Optional[List[Dict[str, Any]]] = None
        self._seed_check: Optional[Dict[str, Any]] = None

    def _certificate(self) -> List[Dict[str, Any]]:
        if self._cert is None:
            self._cert = certificate()
        return self._cert

    def _entry(self, theorem_id: str) -> Dict[str, Any]:
        return next(e for e in self._certificate() if e["id"] == theorem_id)

    # ------------------------------------------------------------ contract

    @property
    def metadata(self) -> SimulationMetadata:
        return SimulationMetadata(
            id="closed_geometry_certificate",
            version="1.0",
            domain="geometric",
            title="Closed Geometry Certificate",
            description=(
                "The topology and leading-order physics of the resolved "
                "Joyce manifold, theorem by theorem, each with its proof, "
                "test and falsifier"),
            section_id="2",
            subsection_id="2.4",
        )

    @property
    def required_inputs(self) -> List[str]:
        """The declared seed: read so it can be checked against the derived
        pair, never used to derive anything."""
        return list(_SEED_INPUTS)

    @property
    def output_params(self) -> List[str]:
        return ["topology.chi_y7"]

    @property
    def output_formulas(self) -> List[str]:
        return [thm.id for thm in THEOREMS]

    def run(self, registry) -> Dict[str, Any]:
        self._cert = certificate()
        self._seed_check = self._compare_seed(registry)
        chi = self._entry("y7-euler-characteristic")
        if not chi["derived"]:
            return {}
        return {"topology.chi_y7": float(chi["evidence"]["chi"])}

    def _compare_seed(self, registry) -> Optional[Dict[str, Any]]:
        """The registry's (b_2, b_3) against the derived pair."""
        betti = self._entry("y7-resolved-betti-numbers")["evidence"]
        if registry is None or not betti["derived"]:
            return None
        declared = tuple(int(registry.get_param(p)) for p in _SEED_INPUTS)
        derived = (betti["betti"][2], betti["betti"][3])
        return {"registry": declared, "derived": derived,
                "agree": declared == derived}

    # ------------------------------------------------------------ formulas

    def get_formulas(self) -> List[Formula]:
        by_id = {thm.id: thm for thm in THEOREMS}
        return [self._formula(by_id[e["id"]], e)
                for e in self._certificate() if e["derived"]]

    @staticmethod
    def _formula(thm: Theorem, entry: Dict[str, Any]) -> Formula:
        ev = entry["evidence"]
        value, spec = thm.track(ev)
        tree, arithma, text, _closed_form = build(spec)
        outputs = (["topology.chi_y7"]
                   if thm.id == "y7-euler-characteristic" else [])
        return Formula(
            id=thm.id,
            label=thm.label,
            latex=thm.latex(ev),
            plain_text=entry["statement"],
            category="DERIVED",
            description=entry["statement"],
            title=thm.title,
            input_params=list(_SEED_INPUTS),
            inputParams=list(_SEED_INPUTS),
            output_params=outputs,
            outputParams=outputs,
            derivation={
                "steps": thm.steps(ev),
                "method": thm.proof,
                "counts": thm.counts,
                "test": thm.test,
                "falsifier": thm.falsifier,
                "scope": thm.scope,
                "holds": entry["holds"],
                "references": [cite(key) for key in thm.references],
            },
            terms=dict(thm.terms),
            eml_tree_str=text,
            eml_description="EML: %s = %g" % (text, value),
            arithma=arithma,
            eml=tree,
            value=value,
        )

    def _chi_eml_text(self) -> str:
        """The chi theorem's own closed form, so the parameter's EML
        description is the same evaluable tree the formula publishes."""
        entry = self._entry("y7-euler-characteristic")
        if not entry["derived"]:
            return "eml_scalar(0)"
        thm = next(t for t in THEOREMS if t.id == entry["id"])
        _value, spec = thm.track(entry["evidence"])
        return build(spec)[2]

    def get_output_param_definitions(self) -> List[Parameter]:
        return [
            Parameter(
                path="topology.chi_y7",
                name="Euler characteristic of Y_7",
                units="dimensionless",
                status="DERIVED",
                description=(
                    "Alternating sum of the Betti numbers of the resolved "
                    "Joyce manifold. Zero, as on every closed odd-dimensional "
                    "manifold; derived here from the resolution rather than "
                    "asserted. Not the effective index chi_eff, whose "
                    "definition is an open ruling."),
                derivation_formula="y7-euler-characteristic",
                no_experimental_value=True,
                eml_description="EML: " + self._chi_eml_text(),
            ),
        ]

    # ------------------------------------------------------------ the paper

    def get_section_content(self) -> Optional[SectionContent]:
        cert = self._certificate()
        blocks = [ContentBlock(
            type="paragraph",
            content=(
                "Every statement in this subsection is rendered from a live "
                "computation, and each names the test that fails if it is "
                "false and the observation that would refute it. Topological "
                "statements hold for either real form of phi; the physics "
                "statements carry their regime."))]
        for entry in cert:
            blocks.append(ContentBlock(type="heading", level=3,
                                       content="%s %s" % (entry["label"],
                                                          entry["title"])))
            blocks.append(ContentBlock(type="paragraph",
                                       content=entry["statement"]))
            if entry["derived"]:
                blocks.append(ContentBlock(type="formula",
                                           formula_id=entry["id"],
                                           label=entry["label"]))
            blocks.append(ContentBlock(
                type="callout", callout_type="info", title="How it could fail",
                content="%s. Scope: %s." % (entry["falsifier"],
                                            entry["scope"])))
        return SectionContent(
            section_id="2",
            subsection_id="2.4",
            title="The Closed Geometry, Theorem by Theorem",
            abstract=(
                "The resolved Joyce manifold's cohomology, Euler "
                "characteristic, singular components, fundamental group, "
                "gauge content and flux potential, each derived and "
                "falsifiable."),
            content_blocks=blocks,
            formula_refs=[e["id"] for e in cert if e["derived"]],
            param_refs=["topology.chi_y7"],
        )

    def get_references(self) -> List[Dict[str, Any]]:
        keys = [key for thm in THEOREMS for key in thm.references]
        return reference_records(keys)

    def get_certificates(self) -> List[Dict[str, Any]]:
        return [{
            "id": "CERT_" + entry["id"].upper().replace("-", "_"),
            "assertion": entry["title"],
            "condition": entry["statement"],
            "tolerance": 0.0,
            "status": "PASS" if entry["holds"] else "FAIL",
            "wolfram_query": None,
            "wolfram_result": "OFFLINE",
            "sector": "foundational",
        } for entry in self._certificate()]

    def get_proofs(self) -> List[Dict[str, Any]]:
        by_id = {thm.id: thm for thm in THEOREMS}
        return [{
            "id": "P_" + entry["id"].upper().replace("-", "_"),
            "theorem": entry["statement"],
            "steps": by_id[entry["id"]].steps(entry["evidence"]),
            "qed": entry["title"] + (" holds." if entry["holds"]
                                     else " does NOT hold on this seed."),
            "simulation_source": self.metadata.id,
        } for entry in self._certificate()]

    def get_learning_materials(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in _LEARNING]

    def validate_self(self) -> Dict[str, Any]:
        checks = [{
            "name": entry["title"],
            "passed": entry["holds"],
            "confidence_interval": {},
            "log_level": "INFO" if entry["holds"] else "ERROR",
            "message": entry["statement"],
        } for entry in self._certificate()]
        seed = self._seed_check
        if seed is not None:
            checks.append({
                "name": "registry seed equals the derived pair",
                "passed": seed["agree"],
                "confidence_interval": {},
                "log_level": "INFO" if seed["agree"] else "ERROR",
                "message": "registry (b_2, b_3) = %s, derived = %s"
                           % (seed["registry"], seed["derived"]),
            })
        return {"passed": all(c["passed"] for c in checks), "checks": checks}
