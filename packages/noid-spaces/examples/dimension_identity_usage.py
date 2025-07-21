#!/usr/bin/env python3
"""
Comprehensive example demonstrating dimension identity and namespacing features.

This example shows:
1. Factory function usage with auto-labeling
2. Dimension creation with proper namespacing
3. JSON-LD serialization and deserialization
4. Transform chain validation
5. Dimension reuse prevention validation
"""

import json

import noid_transforms

from noid_spaces import coordinate_system, from_jsonld, to_jsonld
from noid_spaces.models import CoordinateSystem, CoordinateTransform, Dimension
from noid_spaces.validation import validate_transform_chain


def main():
    print("=== Dimension Identity and Namespacing Examples ===\n")

    # Example 1: Factory function with auto-labeling
    print("1. Factory function with auto-labeling")
    print("-" * 40)

    # Mixed explicit and auto-generated IDs
    raw_data_cs = coordinate_system(
        dimensions=[
            {"id": "x", "unit": "pixel", "type": "space"},  # Explicit ID
            {"unit": "pixel", "type": "space"},  # Auto-labeled as dim_1
            {"id": "time", "unit": "ms", "type": "time"},  # Explicit ID
        ],
        id="raw_acquisition",
        description="Raw microscopy data coordinate system",
    )

    print(f"Raw data coordinate system: {raw_data_cs.id}")
    for i, dim in enumerate(raw_data_cs.dimensions):
        print(f"  Dimension {i}: {dim.id} [{dim.unit.value}] ({dim.type.value})")
    print()

    # Example 2: CoordinateSystem with add_dimension auto-labeling
    print("2. CoordinateSystem with add_dimension auto-labeling")
    print("-" * 50)

    processed_cs = CoordinateSystem(id="processed_data", dimensions=[])
    processed_cs.add_dimension(unit="μm", kind="space", label="x")
    processed_cs.add_dimension(unit="μm", kind="space", label="y")
    processed_cs.add_dimension(unit="ms", kind="time")  # Auto-labeled as dim_2

    print(f"Processed coordinate system: {processed_cs.id}")
    for dim in processed_cs.dimensions:
        print(f"  {dim.id} [{dim.unit.value}] ({dim.type.value})")
    print()

    # Example 3: Type inference
    print("3. Type inference from units")
    print("-" * 30)

    inferred_cs = coordinate_system(
        dimensions=[
            {"id": "width", "unit": "mm"},  # Inferred as SPACE
            {"id": "height", "unit": "mm"},  # Inferred as SPACE
            {"id": "duration", "unit": "s"},  # Inferred as TIME
            {"id": "channel", "unit": "index"},  # Inferred as INDEX
            {"id": "label", "unit": "arbitrary"},  # Inferred as OTHER
        ],
        id="multi_modal",
    )

    print("Type inference results:")
    for dim in inferred_cs.dimensions:
        print(f"  {dim.local_id} ({dim.unit.value}) → {dim.type.value}")
    print()

    # Example 4: JSON-LD serialization with namespaced IDs
    print("4. JSON-LD serialization with namespaced IDs")
    print("-" * 45)

    # Create a coordinate system for JSON-LD demo
    demo_cs = coordinate_system(
        dimensions=[
            {"id": "x", "unit": "mm", "type": "space"},
            {"unit": "mm", "type": "space"},  # Auto-labeled
        ],
        id="demo_system",
    )

    # Serialize to JSON-LD
    jsonld_data = to_jsonld(demo_cs)
    print("JSON-LD serialization:")
    print(json.dumps(jsonld_data, indent=2))

    # Deserialize from JSON-LD
    jsonld_result = from_jsonld(jsonld_data)
    cs_key = [
        k for k in jsonld_result.keys() if k != "@context" and "coordinate-system" in k
    ][0]
    reconstructed_cs = jsonld_result[cs_key]

    print(f"\nReconstructed from JSON-LD: {reconstructed_cs.id}")
    for dim in reconstructed_cs.dimensions:
        print(f"  {dim.id} [{dim.unit.value}] ({dim.type.value})")
    print()

    # Example 5: Transform chain validation
    print("5. Transform chain validation with dimension ID checking")
    print("-" * 55)

    # Create input coordinate system (pixel space)
    input_cs = coordinate_system(
        dimensions=[
            {"id": "x", "unit": "pixel", "type": "space"},
            {"id": "y", "unit": "pixel", "type": "space"},
        ],
        id="pixel_space",
    )

    # Create intermediate coordinate system (mm space)
    intermediate_cs = coordinate_system(
        dimensions=[
            {"id": "x", "unit": "mm", "type": "space"},
            {"id": "y", "unit": "mm", "type": "space"},
        ],
        id="mm_space",
    )

    # Create output coordinate system (world space)
    output_cs = coordinate_system(
        dimensions=[
            {"id": "x", "unit": "mm", "type": "space"},
            {"id": "y", "unit": "mm", "type": "space"},
        ],
        id="world_space",
    )

    # Create transforms
    pixel_to_mm = CoordinateTransform(
        input=input_cs,
        output=intermediate_cs,
        transform=noid_transforms.scale([0.1, 0.1]),  # 0.1mm per pixel
        id="pixel_to_mm",
    )

    mm_to_world = CoordinateTransform(
        input=intermediate_cs,
        output=output_cs,
        transform=noid_transforms.translation([10.0, 20.0]),  # 10mm, 20mm offset
        id="mm_to_world",
    )

    # Validate the transform chain
    try:
        validate_transform_chain([pixel_to_mm, mm_to_world], strict=False)
        print("Transform chain validation passed")
        print(f"  {input_cs.id} → {intermediate_cs.id} → {output_cs.id}")
        print("  Dimension compatibility verified using 4-tier validation logic")
    except Exception as e:
        print(f"Transform chain validation failed: {e}")
    print()

    # Example 6: Dimension reuse prevention
    print("6. Dimension reuse prevention")
    print("-" * 30)

    # This should work - separate dimension objects
    good_cs1 = coordinate_system(
        dimensions=[{"id": "x", "unit": "mm", "type": "space"}], id="system1"
    )
    good_cs2 = coordinate_system(
        dimensions=[{"id": "x", "unit": "mm", "type": "space"}], id="system2"
    )
    print("Created two coordinate systems with separate dimension objects")
    print(f"  System1 dimension: {good_cs1.dimensions[0].id}")
    print(f"  System2 dimension: {good_cs2.dimensions[0].id}")

    # This should fail - reusing dimension objects
    try:
        shared_dim = Dimension(unit="mm", kind="space", dimension_id="shared#x")
        CoordinateSystem(id="bad1", dimensions=[shared_dim])
        CoordinateSystem(id="bad2", dimensions=[shared_dim])  # This will fail
        print("This should not have succeeded")
    except ValueError as e:
        print(f"Correctly prevented dimension reuse: {e}")
    print()

    # Example 7: Coordinate system extraction
    print("7. Coordinate system extraction")
    print("-" * 35)

    from noid_spaces.models import extract_coordinate_system_id

    # All dimensions from same coordinate system
    same_system_dims = good_cs1.dimensions
    extracted_id = extract_coordinate_system_id(same_system_dims)
    print(f"Extracted coordinate system ID: {extracted_id}")

    # Mixed dimensions from different systems
    try:
        mixed_dims = good_cs1.dimensions + good_cs2.dimensions
        extract_coordinate_system_id(mixed_dims)
        print("This should not have succeeded")
    except ValueError as e:
        print(f"Correctly detected mixed coordinate systems: {e}")
    print()

    print("=== All examples completed successfully! ===")


if __name__ == "__main__":
    main()
