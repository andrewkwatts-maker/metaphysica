"""Smoke test: package imports and exposes its declared API."""
import metaphysica


def test_version_present():
    assert isinstance(metaphysica.__version__, str)
    assert len(metaphysica.__version__) > 0


def test_build_callable_exposed():
    assert callable(metaphysica.build)
