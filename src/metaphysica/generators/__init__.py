"""Generators that turn metaphysica.simulations outputs into JSON / JS / HTML / plots.

Every generator is also runnable as a module via
``python -m metaphysica.generators.<name>``. They discover their output
directory via the ``METAPHYSICA_OUT`` environment variable (set by
:func:`metaphysica.build.build`) and fall back to the current working
directory when run standalone.
"""
from metaphysica.generators._common import out_dir, autogen_dir

__all__ = ["out_dir", "autogen_dir"]
