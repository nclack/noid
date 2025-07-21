"""
Tests for dimension identity and namespacing system.

This module tests the RFC-specified dimension identity system including:
- Coordinate system namespacing (coordinate_system#dimension_id)
- Automatic dimension labeling (dim_0, dim_1, etc.)
- Mixed simple and namespaced IDs
- Dimension reuse prevention
"""

import pytest

from noid_spaces.models import CoordinateSystem, Dimension


class TestDimensionIdentityBasics:
    """Test basic dimension identity functionality."""

    def test_standalone_dimension_simple_id(self):
        """Test creating standalone dimension with simple ID."""
        dim = Dimension(unit="mm", dimension_id="x")

        assert dim.id == "x"
        assert dim.local_id == "x"
        assert dim.coordinate_system_id is None
        assert dim.label == "x"

    def test_namespaced_dimension_explicit_id(self):
        """Test creating dimension with namespaced ID."""
        dim = Dimension(unit="mm", dimension_id="system1#x")

        assert dim.id == "system1#x"
        assert dim.local_id == "x"
        assert dim.coordinate_system_id == "system1"
        assert dim.label == "x"

    def test_dimension_with_coordinate_system_object(self):
        """Test creating dimension with coordinate system object."""
        cs = CoordinateSystem(id="test_system", dimensions=[])
        dim = Dimension(unit="mm", label="custom", coordinate_system=cs)

        assert dim.id == "test_system#custom"
        assert dim.local_id == "custom"
        assert dim.coordinate_system_id == "test_system"
        assert dim.label == "custom"

    def test_dimension_id_parsing(self):
        """Test dimension ID parsing functionality."""
        # Namespaced ID
        cs_id, local_id = Dimension.parse_dimension_id("mouse_123#AP")
        assert cs_id == "mouse_123"
        assert local_id == "AP"

        # Simple ID
        cs_id, local_id = Dimension.parse_dimension_id("simple")
        assert cs_id is None
        assert local_id == "simple"

        # Multiple hash symbols (only first is delimiter)
        cs_id, local_id = Dimension.parse_dimension_id("system#dim#extra")
        assert cs_id == "system"
        assert local_id == "dim#extra"


class TestAutomaticDimensionLabeling:
    """Test automatic dimension labeling functionality."""

    def test_auto_labeling_sequential(self):
        """Test sequential automatic labeling."""
        cs = CoordinateSystem(id="test_system", dimensions=[])

        # Add dimensions with auto-labeling
        dim1 = cs.add_dimension(unit="mm", kind="space")
        dim2 = cs.add_dimension(unit="mm", kind="space")
        dim3 = cs.add_dimension(unit="ms", kind="time")

        assert dim1.id == "test_system#dim_0"
        assert dim2.id == "test_system#dim_1"
        assert dim3.id == "test_system#dim_2"

        assert dim1.label == "dim_0"
        assert dim2.label == "dim_1"
        assert dim3.label == "dim_2"

    def test_auto_labeling_with_explicit_labels(self):
        """Test auto-labeling mixed with explicit labels."""
        cs = CoordinateSystem(id="test_system", dimensions=[])

        # Mix auto and explicit labels
        auto_dim1 = cs.add_dimension(unit="mm", kind="space")  # Should be dim_0
        explicit_dim = cs.add_dimension(unit="mm", kind="space", label="custom")
        auto_dim2 = cs.add_dimension(unit="ms", kind="time")  # Should be dim_2

        assert auto_dim1.id == "test_system#dim_0"
        assert explicit_dim.id == "test_system#custom"
        assert auto_dim2.id == "test_system#dim_2"

    def test_auto_labeling_counter_continues(self):
        """Test that auto-labeling counter continues properly."""
        cs = CoordinateSystem(id="test_system", dimensions=[])

        # Add some dimensions
        cs.add_dimension(unit="mm", kind="space")  # dim_0
        cs.add_dimension(unit="mm", kind="space", label="custom")
        cs.add_dimension(unit="ms", kind="time")  # dim_2

        # Add more - should continue counting
        dim4 = cs.add_dimension(unit="arbitrary", kind="other")  # dim_3
        dim5 = cs.add_dimension(unit="index", kind="index")  # dim_4

        assert dim4.id == "test_system#dim_3"
        assert dim5.id == "test_system#dim_4"

    def test_auto_labeling_duplicate_label_prevention(self):
        """Test that duplicate labels are prevented."""
        cs = CoordinateSystem(id="test_system", dimensions=[])

        # Add explicit label
        cs.add_dimension(unit="mm", kind="space", label="dim_1")

        # Auto-labeling should use array index but skip conflicts
        auto_dim1 = cs.add_dimension(
            unit="mm", kind="space"
        )  # Should be dim_1, but that's taken, so dim_2
        auto_dim2 = cs.add_dimension(
            unit="ms", kind="time"
        )  # Should be dim_2, but that's taken, so dim_3

        assert auto_dim1.id == "test_system#dim_2"  # Skipped dim_1 due to conflict
        assert auto_dim2.id == "test_system#dim_3"

    def test_explicit_label_conflicts(self):
        """Test that explicit label conflicts are caught."""
        cs = CoordinateSystem(id="test_system", dimensions=[])

        # Add dimension with explicit label
        cs.add_dimension(unit="mm", kind="space", label="x")

        # Try to add another with same label
        with pytest.raises(ValueError, match="Dimension label 'x' already exists"):
            cs.add_dimension(unit="mm", kind="space", label="x")


class TestMixedIdentityScenarios:
    """Test scenarios mixing different identity approaches."""

    def test_mixed_simple_and_namespaced_dimensions(self):
        """Test using both simple and namespaced dimensions."""
        # Create standalone dimension
        standalone = Dimension(unit="arbitrary", dimension_id="temp_processing")

        # Create coordinate system with namespaced dimensions
        cs = CoordinateSystem(id="microscopy_acquisition", dimensions=[])
        time_dim = cs.add_dimension(unit="ms", kind="time", label="time")
        x_dim = cs.add_dimension(unit="μm", kind="space", label="x")

        # Verify IDs
        assert standalone.id == "temp_processing"
        assert time_dim.id == "microscopy_acquisition#time"
        assert x_dim.id == "microscopy_acquisition#x"

        # All should have different global IDs
        all_ids = {standalone.id, time_dim.id, x_dim.id}
        assert len(all_ids) == 3

    def test_coordinate_system_from_existing_dimensions(self):
        """Test creating coordinate system from pre-existing dimensions."""
        # Create dimensions first
        x_dim = Dimension(unit="mm", dimension_id="system1#x")
        y_dim = Dimension(unit="mm", dimension_id="system1#y")

        # Create coordinate system
        cs = CoordinateSystem(id="system1", dimensions=[x_dim, y_dim])

        assert len(cs.dimensions) == 2
        assert cs.dimensions[0].id == "system1#x"
        assert cs.dimensions[1].id == "system1#y"

    def test_dimension_ownership_validation(self):
        """Test that dimensions must belong to the same coordinate system."""
        # Create dimensions for different coordinate systems
        dim1 = Dimension(unit="mm", dimension_id="system1#x")
        dim2 = Dimension(unit="mm", dimension_id="system2#y")  # Different system

        # Should fail to create coordinate system with mismatched dimensions
        with pytest.raises(
            ValueError,
            match="belongs to coordinate system 'system2'.*but this coordinate system is 'system1'",
        ):
            CoordinateSystem(id="system1", dimensions=[dim1, dim2])


class TestDimensionIdentityEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_coordinate_system_auto_labeling(self):
        """Test auto-labeling works with initially empty coordinate system."""
        cs = CoordinateSystem(id="empty_system", dimensions=[])

        # Should start with dim_0
        first_dim = cs.add_dimension(unit="mm", kind="space")
        assert first_dim.id == "empty_system#dim_0"

        # Add more
        second_dim = cs.add_dimension(unit="s", kind="time")
        assert second_dim.id == "empty_system#dim_1"

    def test_dimension_without_coordinate_system_or_id(self):
        """Test that dimension requires either coordinate_system or dimension_id."""
        with pytest.raises(
            ValueError,
            match="Must provide either 'dimension_id' or 'coordinate_system'",
        ):
            Dimension(unit="mm", kind="space")

    def test_dimension_with_both_coordinate_system_and_id(self):
        """Test dimension creation with both coordinate_system and dimension_id."""
        cs = CoordinateSystem(id="test_system", dimensions=[])

        # Should use dimension_id over coordinate_system when both provided
        dim = Dimension(
            unit="mm",
            kind="space",
            coordinate_system=cs,  # This should be ignored
            dimension_id="standalone#custom",
        )

        assert dim.id == "standalone#custom"
        assert dim.coordinate_system_id == "standalone"
        assert dim.local_id == "custom"

    def test_empty_dimension_id_rejected(self):
        """Test that empty dimension_id is properly rejected."""
        with pytest.raises(
            ValueError,
            match="Must provide either 'dimension_id' or 'coordinate_system'",
        ):
            Dimension(unit="mm", dimension_id="")

        with pytest.raises(
            ValueError,
            match="Must provide either 'dimension_id' or 'coordinate_system'",
        ):
            Dimension(unit="mm", dimension_id="   ")  # Whitespace only

    def test_coordinate_system_none_id_with_auto_labeling(self):
        """Test coordinate system with None id and auto-labeling."""
        cs = CoordinateSystem(id=None, dimensions=[])

        # Auto-labeling should still work, but with None as coordinate system ID
        dim = cs.add_dimension(unit="mm", kind="space")

        # Should have local label but no coordinate system prefix
        assert dim.coordinate_system_id is None
        assert dim.label == "dim_0"
        assert dim.id == "dim_0"  # No coordinate system prefix


class TestDimensionIdentityIntegration:
    """Test integration scenarios with the dimension identity system."""

    def test_realistic_microscopy_scenario(self):
        """Test realistic microscopy coordinate system scenario."""
        # Create microscopy acquisition coordinate system
        microscopy_cs = CoordinateSystem(id="microscopy_acquisition", dimensions=[])

        # Add spatial dimensions with explicit labels
        x_dim = microscopy_cs.add_dimension(unit="μm", kind="space", label="x")
        y_dim = microscopy_cs.add_dimension(unit="μm", kind="space", label="y")
        z_dim = microscopy_cs.add_dimension(unit="μm", kind="space", label="z")

        # Add time dimension
        time_dim = microscopy_cs.add_dimension(unit="ms", kind="time", label="time")

        # Add channel dimension (auto-labeled)
        channel_dim = microscopy_cs.add_dimension(unit="arbitrary", kind="other")

        # Verify all IDs
        assert x_dim.id == "microscopy_acquisition#x"
        assert y_dim.id == "microscopy_acquisition#y"
        assert z_dim.id == "microscopy_acquisition#z"
        assert time_dim.id == "microscopy_acquisition#time"
        assert (
            channel_dim.id == "microscopy_acquisition#dim_4"
        )  # Auto-labeled (5th dimension, index 4)

        # Verify coordinate system
        assert len(microscopy_cs.dimensions) == 5

        # Test string representation
        cs_str = str(microscopy_cs)
        assert "microscopy_acquisition" in cs_str
        assert "5 dims" in repr(microscopy_cs)

    def test_mixed_processing_pipeline_scenario(self):
        """Test realistic processing pipeline with mixed dimension types."""
        # Create raw acquisition coordinate system
        raw_cs = CoordinateSystem(id="raw_data", dimensions=[])
        raw_x = raw_cs.add_dimension(unit="pixel", kind="space", label="x")
        raw_y = raw_cs.add_dimension(unit="pixel", kind="space", label="y")

        # Create processed coordinate system
        processed_cs = CoordinateSystem(id="processed_data", dimensions=[])
        proc_x = processed_cs.add_dimension(unit="μm", kind="space", label="x")
        proc_y = processed_cs.add_dimension(unit="μm", kind="space", label="y")

        # Create temporary processing dimensions (standalone)
        temp_dim1 = Dimension(unit="arbitrary", dimension_id="temp_buffer_1")
        temp_dim2 = Dimension(unit="arbitrary", dimension_id="temp_buffer_2")

        # Verify all have unique global IDs
        all_ids = {raw_x.id, raw_y.id, proc_x.id, proc_y.id, temp_dim1.id, temp_dim2.id}
        assert len(all_ids) == 6

        # Verify namespacing works correctly
        assert raw_x.id == "raw_data#x"
        assert proc_x.id == "processed_data#x"  # Same local ID, different global ID
        assert temp_dim1.id == "temp_buffer_1"  # Simple ID

    def test_serialization_preserves_identity(self):
        """Test that serialization preserves dimension identity."""
        # Create coordinate system with mixed labeling
        cs = CoordinateSystem(id="test_serialization", dimensions=[])
        auto_dim = cs.add_dimension(unit="mm", kind="space")
        explicit_dim = cs.add_dimension(unit="s", kind="time", label="duration")

        # Test dimension serialization
        auto_data = auto_dim.to_data()
        explicit_data = explicit_dim.to_data()

        assert auto_data["id"] == "test_serialization#dim_0"
        assert explicit_data["id"] == "test_serialization#duration"

        # Test deserialization preserves identity
        auto_restored = Dimension.from_data(auto_data)
        explicit_restored = Dimension.from_data(explicit_data)

        assert auto_restored.id == auto_dim.id
        assert explicit_restored.id == explicit_dim.id
        assert auto_restored.coordinate_system_id == "test_serialization"
        assert explicit_restored.coordinate_system_id == "test_serialization"
