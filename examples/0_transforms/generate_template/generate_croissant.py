#!/usr/bin/env python3
"""
Generate a valid croissant file for transform examples using mlcroissant API.
"""

import mlcroissant as mlc
from pathlib import Path
import json
import hashlib
from datetime import datetime


def generate_croissant_dataset():
    """Generate a valid croissant dataset for transform examples using mlcroissant API."""

    # Create context
    ctx = mlc.Context()

    # Calculate hash of the table file
    table_path = Path(__file__).parent / "transforms_table.json"
    with open(table_path, "rb") as f:
        content = f.read()
        sha256_hash = hashlib.sha256(content).hexdigest()

    # Create file object
    file_object = mlc.FileObject(
        ctx=ctx,
        id="table",
        name="transforms_table.json",
        description="Table containing transform examples with parameters",
        content_url="transforms_table.json",
        encoding_formats=["application/json"],
        sha256=sha256_hash,
    )

    # Create fields
    id_field = mlc.Field(
        ctx=ctx,
        name="id",
        description="Unique identifier for the transform",
        data_types=[mlc.DataType.TEXT],
        source=mlc.Source(
            ctx=ctx, file_object="table", extract=mlc.Extract(ctx=ctx, column="id")
        ),
    )

    label_field = mlc.Field(
        ctx=ctx,
        name="label",
        description="Human readable description of the transform",
        data_types=[mlc.DataType.TEXT],
        source=mlc.Source(
            ctx=ctx, file_object="table", extract=mlc.Extract(ctx=ctx, column="label")
        ),
    )

    # Create record set
    record_set = mlc.RecordSet(
        ctx=ctx,
        name="transforms",
        description="Transform examples with their parameters",
        fields=[id_field, label_field],
    )

    # Create metadata
    metadata = mlc.Metadata(
        ctx=ctx,
        name="noid-transform-examples",
        description="Example coordinate transformations for multidimensional arrays",
        cite_as="@misc{noid-transforms, title={NOID Transform Examples}, author={Nathan Clack}, year={2025}}",
        license=["https://creativecommons.org/licenses/by/4.0/"],
        url="https://github.com/nclack/noid/examples/transforms.json",
        version="1.0.0",
        date_published=datetime(2025, 1, 13),
        distribution=[file_object],
        record_sets=[record_set],
    )

    return metadata


def main():
    """Generate and save the croissant dataset."""
    metadata = generate_croissant_dataset()
    print(metadata.issues.report())
    output_path = Path(__file__).parent / "transforms_generated.json"

    # Convert to JSON and save
    json_data = metadata.to_json()

    # Custom JSON encoder for datetime objects
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    with open(output_path, "w") as f:
        json.dump(json_data, f, indent=2, default=json_serial)

    print(f"Generated croissant file: {output_path}")
    print("To validate: uv run mlcroissant validate --jsonld transforms_generated.json")


if __name__ == "__main__":
    main()
