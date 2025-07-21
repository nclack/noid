#!/usr/bin/env python3
"""
Usage examples for the transforms library.

This script demonstrates how to use the transforms library to create,
validate, and serialize coordinate transformations.
"""

import noid_transforms as transforms


def basic_usage() -> None:
    """Demonstrate basic transform creation and usage."""
    print("=== Basic Transform Creation ===")

    # Create different types of transforms
    identity = transforms.identity()
    translation = transforms.translation([10, 20, 5])
    scale = transforms.scale([2.0, 1.5, 0.5])
    mapaxis = transforms.mapaxis([1, 0, 2])

    # Create a homogeneous matrix
    matrix = [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
    homogeneous = transforms.homogeneous(matrix)

    # Create lookup table transforms
    displacement = transforms.displacements(
        "path/to/displacement_field.zarr", interpolation="linear", extrapolation="zero"
    )

    coordinate_lut = transforms.coordinate_lookup(
        "path/to/coordinate_lut.zarr", interpolation="cubic", extrapolation="reflect"
    )

    # Display transforms
    print(f"Identity: {identity}")
    print(f"Translation: {translation}")
    print(f"Scale: {scale}")
    print(f"MapAxis: {mapaxis}")
    print(f"Homogeneous: {homogeneous}")
    print(f"Displacement LUT: {displacement}")
    print(f"Coordinate LUT: {coordinate_lut}")
    print()


def factory_usage() -> None:
    """Demonstrate factory function usage."""
    print("=== Factory Function Usage ===")

    # Create transforms from dictionaries
    transforms_data = [
        "identity",
        {"translation": [10, 20, 5]},
        {"scale": [2.0, 1.5, 0.5]},
        {"map-axis": [1, 0, 2]},
        {
            "homogeneous": [
                [2.0, 0, 0, 10],
                [0, 1.5, 0, 20],
                [0, 0, 0.5, 5],
                [0, 0, 0, 1],
            ]
        },
        {"displacements": "path/to/displacement_field.zarr"},
        {
            "displacements": {
                "path": "path/to/field.zarr",
                "interpolation": "linear",
                "extrapolation": "zero",
            }
        },
        {
            "lookup-table": {
                "path": "path/to/coordinate_lut.zarr",
                "interpolation": "cubic",
                "extrapolation": "reflect",
            }
        },
    ]

    # Create transforms from data
    transform_objects = []
    for data in transforms_data:
        transform = transforms.from_data(data)
        transform_objects.append(transform)
        print(f"Created {type(transform).__name__}: {transform}")

    # Create from JSON
    json_data = '{"translation": [10, 20, 5]}'
    from_json = transforms.from_json(json_data)
    print(f"From JSON: {from_json}")

    # Create sequence using list comprehension
    sequence = [transforms.from_data(data) for data in transforms_data]
    print(f"Sequence length: {len(sequence)}")
    print()


def serialization_usage() -> None:
    """Demonstrate serialization capabilities."""
    print("=== Serialization Usage ===")

    # Create a sample transform
    translation = transforms.translation([10, 20, 5])

    # Serialize to different formats
    dict_repr = transforms.to_data(translation)
    json_repr = transforms.to_json(translation, indent=2)
    jsonld_repr = transforms.to_jsonld(translation, indent=2)

    print("Dictionary representation:")
    print(dict_repr)
    print()

    print("JSON representation:")
    print(json_repr)
    print()

    print("JSON-LD representation:")
    print(jsonld_repr)
    print()

    # Serialize a sequence
    sequence = [
        transforms.identity(),
        transforms.translation([10, 20, 5]),
        transforms.scale([2.0, 1.5, 0.5]),
    ]

    # Serialize sequences directly using to_json and to_jsonld
    json_sequence = transforms.to_json(sequence, indent=2)
    jsonld_sequence = transforms.to_jsonld(sequence, indent=2)

    print("JSON sequence:")
    print(json_sequence)
    print()

    print("JSON-LD sequence:")
    print(jsonld_sequence)
    print()


def validation_usage() -> None:
    """Demonstrate validation capabilities."""
    print("=== Validation Usage ===")

    # Create valid transforms
    valid_transforms = [
        transforms.identity(),
        transforms.translation([10, 20, 5]),
        transforms.scale([2.0, 1.5, 0.5]),
        transforms.mapaxis([1, 0, 2]),
    ]

    # Validate individual transforms
    for transform in valid_transforms:
        is_valid = transforms.validate(transform)
        print(f"{type(transform).__name__}: valid = {is_valid}")

    # Validate sequence using all()
    sequence_valid = all(transforms.validate(t) for t in valid_transforms)
    print(f"Sequence valid: {sequence_valid}")

    # Check dimension consistency
    consistent = transforms.validate_dimension_consistency(valid_transforms)
    print(f"Dimension consistency: {consistent}")

    # Test error handling
    try:
        # This should fail - duplicate indices
        invalid_mapaxis = transforms.mapaxis([1, 0, 1])
        transforms.validate(invalid_mapaxis)
    except transforms.ValidationError as e:
        print(f"Validation error (expected): {e}")

    print()


def jsonld_examples() -> None:
    """Demonstrate JSON-LD specific features with enhanced PyLD processing."""
    print("=== JSON-LD Examples ===")

    # Create transforms with semantic context
    translation = transforms.translation([10, 20, 5])
    scale = transforms.scale([2.0, 1.5, 0.5])

    # Create JSON-LD with and without context
    jsonld_with_context = transforms.to_jsonld(translation, include_context=True)
    jsonld_without_context = transforms.to_jsonld(translation, include_context=False)

    print("JSON-LD with context:")
    print(jsonld_with_context)
    print()

    print("JSON-LD without context:")
    print(jsonld_without_context)
    print()

    # Demonstrate dictionary serialization with namespace abbreviations
    transforms_dict = {
        "my_translation": translation,
        "my_scale": scale,
    }

    jsonld_dict = transforms.to_jsonld(transforms_dict, include_context=True)
    print("JSON-LD dictionary with namespace abbreviations:")
    print(jsonld_dict)
    print()

    # Demonstrate sequence serialization using JSON-LD @list construct
    sequence = [translation, scale]
    jsonld_sequence = transforms.to_jsonld(sequence, include_context=True)
    print("JSON-LD sequence using @list construct:")
    print(jsonld_sequence)
    print()

    # Round-trip through JSON-LD
    recreated = transforms.from_jsonld(jsonld_with_context)
    print(f"from_jsonld returned: {type(recreated)} = {recreated}")

    # Simple round-trip test - just check if we got something back
    round_trip_success = recreated is not None
    print(f"Round-trip successful: {round_trip_success}")
    print()

    # Demonstrate enhanced JSON-LD processing with custom context
    custom_jsonld = {
        "@context": {
            "tr": "https://github.com/nclack/noid/schemas/transforms/",
            "custom": "https://example.com/custom/",
        },
        "tr:translation": [10, 20, 5],
        "custom:metadata": {"description": "Example transform"},
    }

    try:
        processed = transforms.from_jsonld(custom_jsonld)
        print("Enhanced JSON-LD processing with custom context:")
        print(f"Processed result: {processed}")
        print()
    except Exception as e:
        print(f"Enhanced processing error (expected if PyLD not available): {e}")
        print()

    # Demonstrate legacy JSON-LD format still works
    legacy_json = '{"translation": [10, 20, 5]}'
    try:
        legacy_result = transforms.from_json(legacy_json)
        if hasattr(legacy_result, "to_data"):
            print(f"Legacy format support: {legacy_result.to_data()}")
        else:
            print(f"Legacy format support: {legacy_result}")
    except Exception as e:
        print(f"Legacy format error: {e}")
    print()


def advanced_usage() -> None:
    """Demonstrate advanced features."""
    print("=== Advanced Usage ===")

    # Transform properties
    translation = transforms.translation([10, 20, 5])
    print(f"Translation dimensions: {translation.dimensions}")

    scale = transforms.scale([2.0, 1.5, 0.5])
    print(f"Scale dimensions: {scale.dimensions}")

    mapaxis = transforms.mapaxis([1, 0, 2])
    print(f"MapAxis input dimensions: {mapaxis.input_dimensions}")
    print(f"MapAxis output dimensions: {mapaxis.output_dimensions}")

    # Homogeneous matrix utilities
    matrix = [[2.0, 0, 0, 10], [0, 1.5, 0, 20], [0, 0, 0.5, 5], [0, 0, 0, 1]]
    homogeneous = transforms.homogeneous(matrix)
    print(f"Homogeneous matrix shape: {homogeneous.matrix_shape}")
    print(f"Retrieved matrix: {homogeneous.get_matrix()}")

    # Transform compatibility
    compatible = transforms.check_transform_compatibility(translation, scale)
    print(f"Translation/Scale compatibility: {compatible}")

    mapaxis_2d = transforms.mapaxis([1, 0])
    incompatible = transforms.check_transform_compatibility(mapaxis_2d, translation)
    print(f"2D MapAxis/3D Translation compatibility: {incompatible}")

    print()


def main() -> None:
    """Run all examples."""
    print("Transforms Library Usage Examples")
    print("=" * 50)
    print()

    basic_usage()
    factory_usage()
    serialization_usage()
    validation_usage()
    jsonld_examples()
    advanced_usage()

    print("Examples completed successfully!")


if __name__ == "__main__":
    main()
