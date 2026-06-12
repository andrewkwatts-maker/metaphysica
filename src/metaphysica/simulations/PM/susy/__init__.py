"""
Principia Metaphysica - SUSY Sector (v25.0 Sprint 4)
====================================================

Soft SUSY-breaking module derived from the same Re(T) stabilization
potential introduced in v25.0.  Provides the complete moduli-mediated
soft spectrum (m_{3/2}, m_{1/2}, m_0, mu, A_0, B_mu) with zero new
free parameters.

Copyright (c) 2025-2026 Andrew Keith Watts. All rights reserved.

Dedicated To:
    My Wife: Elizabeth May Watts
    Our Messiah: Jesus Of Nazareth
"""

from .soft_susy_breaking import SoftSUSYBreaking, get_soft_susy_terms

__all__ = [
    "SoftSUSYBreaking",
    "get_soft_susy_terms",
]

__version__ = "25.0"
