"""Pytest configuration and fixtures for noid-spaces tests."""

import pytest

@pytest.fixture
def sample_dimension():
    """Create a sample dimension for testing."""
    from noid_spaces.models import Dimension
    return Dimension(id="x", unit="micrometer", type="space")

@pytest.fixture
def sample_dimensions():
    """Create sample dimensions for testing coordinate systems."""
    from noid_spaces.models import Dimension
    return [
        Dimension(id="x", unit="micrometer", type="space"),
        Dimension(id="y", unit="micrometer", type="space"),
        Dimension(id="t", unit="second", type="time"),
    ]

@pytest.fixture
def sample_coordinate_system():
    """Create a sample coordinate system for testing."""
    from noid_spaces.models import CoordinateSystem, Dimension
    dimensions = [
        Dimension(id="x", unit="micrometer", type="space"),
        Dimension(id="y", unit="micrometer", type="space"),
    ]
    return CoordinateSystem(id="physical", dimensions=dimensions)

@pytest.fixture
def sample_index_dimensions():
    """Create sample index dimensions for testing."""
    from noid_spaces.models import Dimension
    return [
        Dimension(id="i", unit="index", type="index"),
        Dimension(id="j", unit="index", type="index"),
        Dimension(id="k", unit="index", type="index"),
    ]
