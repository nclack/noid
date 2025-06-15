#!/usr/bin/env python3
"""
Example script demonstrating recordset concept with transform examples.
Shows how croissant recordsets work.
"""

import json
from pathlib import Path
from rich.console import Console
from rich.text import Text
import mlcroissant as mlc

console = Console()


def load_recordset():
    """Load transforms recordset using mlcroissant"""
    examples_dir = Path(__file__).parent
    croissant_file = examples_dir / "transforms.json"
    
    dataset = mlc.Dataset(croissant_file)
    return list(dataset.records(record_set="transforms"))


def get_transform_color(param_key):
    """Get color for transform type"""
    colors = {
        "translation": "green",
        "scale": "blue",
        "matrix": "magenta",
        "mapAxis": "yellow",
        "displacements": "red",
        "coordinates": "bright_blue",
    }
    return colors.get(param_key, "white")


def format_parameter_value(value):
    """Format parameter value with appropriate styling"""
    if isinstance(value, list):
        # Handle nested arrays (like matrices)
        if value and isinstance(value[0], list):
            # Matrix format - show dimensions
            rows = len(value)
            cols = len(value[0]) if value else 0
            return Text(f"[{rows}x{cols} matrix]", style="dim italic")
        else:
            # Simple array
            json_str = json.dumps(value, separators=(",", ":"))
            return Text(json_str, style="cyan")
    elif isinstance(value, dict):
        return Text(json.dumps(value, separators=(",", ":")), style="yellow")
    else:
        return Text(str(value), style="cyan")


def main():
    console.print("Transform Examples via RecordSet:", style="bold magenta")
    console.print("(Using mlcroissant to load recordset)", style="italic")
    console.print("=" * 50, style="dim")

    # Load recordset using mlcroissant
    transforms_recordset = load_recordset()

    for i, record in enumerate(transforms_recordset):
        console.print()

        # Transform number and name
        name_text = Text(f"{i + 1}. ")
        name_text.append(
            record.get("label", "Unnamed transform"), style="bold bright_white"
        )
        console.print(name_text)

        # ID
        id_text = Text("   ID: ", style="white")
        id_text.append(record.get("id", "N/A"), style="white")
        console.print(id_text)

        # Display parameters based on what's present
        param_keys = [
            "translation",
            "scale",
            "matrix",
            "mapAxis",
            "displacements",
            "coordinates",
        ]

        param_found = False
        for key in param_keys:
            if key in record and record[key] is not None:
                value = record[key]

                # Parameter type with color
                param_text = Text("   Transform type: ", style="white")
                param_text.append(key, style=get_transform_color(key))
                console.print(param_text)

                # Parameter value
                value_text = Text("   Parameters: ", style="white")
                value_text.append(format_parameter_value(value))
                console.print(value_text)

                param_found = True
                break  # Only show the main parameter for each transform

        # If no parameters found, it's probably identity
        if not param_found:
            param_text = Text("   Transform type: ", style="white")
            param_text.append("identity", style="bright_green")
            console.print(param_text)
            console.print("   [dim italic](no parameters)[/dim italic]")

    console.print()
    console.print(
        f"[bold]Total transforms: [bright_magenta]{len(transforms_recordset)}[/bright_magenta][/bold]"
    )


if __name__ == "__main__":
    main()
