#!/usr/bin/env -S uv run
# /// script
# dependencies = ["mlcroissant", "rich", "noid"]
# ///

import json
import os
from rich.console import Console
from rich.table import Table
import mlcroissant as mlc
from noid import Transform


def display_transforms():
    console = Console()

    # Load the dataset using mlcroissant
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, "transforms.json")
    dataset = mlc.Dataset(dataset_path)

    # Create table
    table = Table(title="Transform Examples with Validation")
    table.add_column("ID", style="cyan")
    table.add_column("Label", style="magenta")
    table.add_column("Transform", style="yellow")

    # Add rows from the recordset
    recordset_names = [rs.uuid for rs in dataset.metadata.record_sets]
    for record in dataset.records(recordset_names[0]):
        record_id = record["records1/id"].decode()
        record_label = record["records1/label"].decode()
        transform_json = record["records1/transform"].decode()

        # Parse and validate with Transform
        transform_data = json.loads(transform_json)
        transform_obj = Transform(transform_data)
        pretty_transform = transform_obj.model_dump_json(indent=2)

        table.add_row(record_id, record_label, pretty_transform)

    console.print(table)


if __name__ == "__main__":
    display_transforms()
