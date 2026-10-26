"""Path audit: generic checks over run outputs and fork selections.

Pure functions over plain data (selections and row maps); no theory knowledge.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.
"""

from metaphysica.testground.audit.classes import RunClass, equivalence_classes
from metaphysica.testground.audit.interactions import (
    footprints,
    interaction_sets,
    non_additive,
    predict,
)
from metaphysica.testground.audit.noop import no_op_options
from metaphysica.testground.audit.reads import ReadFindings, reconcile_reads
from metaphysica.testground.audit.report import audit, to_markdown
from metaphysica.testground.audit.rows import changed, differs, load_rows
from metaphysica.testground.audit.sampling import sample_selections

__all__ = [
    "RunClass", "equivalence_classes", "footprints", "interaction_sets",
    "non_additive", "predict", "no_op_options", "ReadFindings",
    "reconcile_reads", "audit", "to_markdown", "changed", "differs",
    "load_rows", "sample_selections",
]
