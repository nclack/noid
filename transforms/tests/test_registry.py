"""
Tests for the registry system.

This module tests the core registry functionality including namespace management,
factory registration, and error handling.
"""

import pytest

# Test the registry system
from noid_transforms.registry import (
    FactoryValidationError,
    Registry,
    UnknownIRIError,
    register,
    registry,
    set_namespace,
)


# Mock transform classes for testing
class MockTransform:
    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        return isinstance(other, MockTransform) and self.data == other.data


class MockTranslation(MockTransform):
    pass


class MockScale(MockTransform):
    pass


class TestNamespaceContext:
    """Test thread-local namespace context management."""

    def test_set_namespace_basic(self):
        """Test setting namespace."""
        set_namespace("https://example.com/schemas/")

        # Test that we can register a function
        test_registry = Registry()

        @test_registry.register
        def test_transform(data: list[float]) -> MockTransform:
            return MockTransform(data)

        # Check that the IRI was built correctly
        expected_iri = "https://example.com/schemas/test_transform"
        assert expected_iri in test_registry.get_registered_iris()

    def test_set_namespace_path_handling(self):
        """Test namespace path handling."""
        set_namespace("https://github.com/example/schemas/transforms/")

        test_registry = Registry()

        @test_registry.register
        def another_transform(data: str) -> MockTransform:
            return MockTransform(data)

        # Should handle trailing slash correctly
        expected_iri = "https://github.com/example/schemas/transforms/another_transform"
        assert expected_iri in test_registry.get_registered_iris()

    def test_collision_detection(self):
        """Test that duplicate IRI registration is prevented."""
        set_namespace("https://collision.test/")
        test_registry = Registry()

        # Register first function
        @test_registry.register
        def transform1(data) -> MockTransform:
            return MockTransform(data)

        # Should have been registered successfully
        assert (
            "https://collision.test/transform1" in test_registry.get_registered_iris()
        )

        # Try to register different function with same name - should fail
        def different_transform(data) -> MockTransform:
            return MockTransform(f"different_{data}")

        with pytest.raises(
            RuntimeError, match="already registered with a different factory"
        ):
            test_registry.register("transform1")(different_transform)

    def test_namespace_collision_across_registries(self):
        """Test that different registries can have same namespaces without collision."""
        # This demonstrates that collisions are per-registry, not global
        set_namespace("https://shared.test/")

        registry1 = Registry()
        registry2 = Registry()

        # Both registries can register the same name independently
        @registry1.register
        def shared_transform(data) -> MockTransform:
            return MockTransform(f"registry1_{data}")

        @registry2.register
        def shared_transform(data) -> MockTransform:
            return MockTransform(f"registry2_{data}")

        # Both should be registered in their respective registries
        assert "https://shared.test/shared_transform" in registry1.get_registered_iris()
        assert "https://shared.test/shared_transform" in registry2.get_registered_iris()

        # But they should create different objects
        obj1 = registry1.create("https://shared.test/shared_transform", "test")
        obj2 = registry2.create("https://shared.test/shared_transform", "test")

        assert obj1.data == "registry1_test"
        assert obj2.data == "registry2_test"

    def test_namespace_management(self):
        """Test namespace setting and IRI construction."""
        # Create a separate registry to test namespace management
        test_registry = Registry()

        # Test setting a custom namespace
        set_namespace("https://custom.test/schemas/")

        @test_registry.register
        def custom_transform(data) -> MockTransform:
            return MockTransform(data)

        # Should be registered with custom namespace
        iris = test_registry.get_registered_iris()
        assert "https://custom.test/schemas/custom_transform" in iris

        # Test different namespace
        set_namespace("https://example.com/schemas/widgets/")

        @test_registry.register
        def widget_transform(data) -> MockTransform:
            return MockTransform(data)

        # Should be registered with new namespace
        iris = test_registry.get_registered_iris()
        assert "https://example.com/schemas/widgets/widget_transform" in iris


class TestFactoryRegistration:
    """Test factory function registration and creation."""

    def setup_method(self):
        """Set up test environment."""
        set_namespace("https://test.com/schemas/")
        self.registry = Registry()

    def test_basic_registration(self):
        """Test basic factory registration."""

        @self.registry.register
        def translation(data: list[float]) -> MockTranslation:
            return MockTranslation(data)

        # Test creation
        result = self.registry.create("https://test.com/schemas/translation", [1, 2, 3])
        assert isinstance(result, MockTranslation)
        assert result.data == [1, 2, 3]

    def test_name_override_registration(self):
        """Test registration with name override."""

        @self.registry.register("map-axis")  # Override snake_case → kebab-case
        def map_axis(data: list[int]) -> MockTransform:
            return MockTransform(data)

        # Should be registered with override name
        result = self.registry.create("https://test.com/schemas/map-axis", [0, 1, 2])
        assert isinstance(result, MockTransform)
        assert result.data == [0, 1, 2]

    def test_decorator_syntax_variants(self):
        """Test different decorator syntax variants."""

        # @register (no parentheses)
        @self.registry.register
        def variant1(data) -> MockTransform:
            return MockTransform(data)

        # @register() (empty parentheses)
        @self.registry.register()
        def variant2(data) -> MockTransform:
            return MockTransform(data)

        # @register("name") (with override)
        @self.registry.register("variant3_override")
        def variant3(data) -> MockTransform:
            return MockTransform(data)

        # All should be registered
        iris = self.registry.get_registered_iris()
        assert "https://test.com/schemas/variant1" in iris
        assert "https://test.com/schemas/variant2" in iris
        assert "https://test.com/schemas/variant3_override" in iris
        assert len(iris) == 3

    def test_type_to_iri_mapping(self):
        """Test type to IRI mapping for serialization."""

        @self.registry.register
        def translation(data: list[float]) -> MockTranslation:
            return MockTranslation(data)

        # Create object
        obj = self.registry.create("https://test.com/schemas/translation", [1, 2, 3])

        # Test reverse lookup from object to IRI
        iri = self.registry.get_iri_for_object(obj)
        assert iri == "https://test.com/schemas/translation"


class TestErrorHandling:
    """Test registry error handling and suggestions."""

    def setup_method(self):
        set_namespace("https://test.com/schemas/")
        self.registry = Registry()

        # Register some transforms for testing
        @self.registry.register
        def translation(data) -> MockTranslation:
            return MockTranslation(data)

        @self.registry.register
        def scale(data) -> MockScale:
            return MockScale(data)

    def test_unknown_transform_error(self):
        """Test error for unknown transform IRI."""
        with pytest.raises(UnknownIRIError) as exc_info:
            self.registry.create("https://test.com/schemas/unknown", [1, 2, 3])

        error = exc_info.value
        assert error.iri == "https://test.com/schemas/unknown"
        assert len(error.available) > 0
        assert "Unknown IRI" in str(error)

    def test_unknown_transform_error_clean_message(self):
        """Test clean error messages for unknown transforms."""
        with pytest.raises(UnknownIRIError) as exc_info:
            self.registry.create(
                "https://test.com/schemas/unknown_transform", [1, 2, 3]
            )

        error = exc_info.value
        error_msg = str(error)
        # Should provide clean error message
        assert "Unknown IRI: 'https://test.com/schemas/unknown_transform'" in error_msg

    def test_factory_validation_error(self):
        """Test error when factory function fails."""

        @self.registry.register
        def failing_transform(data) -> MockTransform:
            raise ValueError("Factory failed!")

        with pytest.raises(FactoryValidationError) as exc_info:
            self.registry.create(
                "https://test.com/schemas/failing_transform", [1, 2, 3]
            )

        error = exc_info.value
        assert error.iri == "https://test.com/schemas/failing_transform"
        assert error.data == [1, 2, 3]
        assert "Factory for" in str(error)
        assert "failed with data" in str(error)


class TestRegistryIntegration:
    """Test integration with the global registry."""

    def test_global_registry_usage(self):
        """Test using the global registry instance."""
        # Should be able to use the global registry
        assert registry is not None
        assert hasattr(registry, "create")
        assert hasattr(registry, "register")

    def test_registration_persistence(self):
        """Test that registrations persist in global registry."""
        # Register something in global registry
        set_namespace("https://global.test/")

        @register
        def persistent_transform(data: str) -> MockTransform:
            return MockTransform(data)

        # Should be able to create it
        result = registry.create(
            "https://global.test/persistent_transform", "test_data"
        )
        assert isinstance(result, MockTransform)
        assert result.data == "test_data"

        # Should appear in registered IRIs
        assert (
            "https://global.test/persistent_transform" in registry.get_registered_iris()
        )


class TestRegistryInspection:
    """Test registry inspection capabilities."""

    def setup_method(self):
        set_namespace("https://inspect.test/")
        self.registry = Registry()

        @self.registry.register
        def transform1(data) -> MockTranslation:
            return MockTranslation(data)

        @self.registry.register
        def transform2(data) -> MockScale:
            return MockScale(data)

    def test_get_registered_iris(self):
        """Test getting all registered IRIs."""
        iris = self.registry.get_registered_iris()

        assert "https://inspect.test/transform1" in iris
        assert "https://inspect.test/transform2" in iris
        assert len(iris) == 2

    def test_get_registered_types(self):
        """Test getting all registered types."""
        types = self.registry.get_registered_types()

        assert MockTranslation in types
        assert MockScale in types
        assert len(types) == 2


if __name__ == "__main__":
    pytest.main([__file__])
