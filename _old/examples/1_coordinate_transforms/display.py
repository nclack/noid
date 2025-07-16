#!/usr/bin/env python3
"""Display coordinate transforms from croissant recordset using rich formatting."""

import mlcroissant as mlc
from rich.console import Console
from rich.table import Table
from pathlib import Path


def load_croissant_dataset():
    """Load the croissant dataset from the current directory."""
    croissant_path = Path(__file__).parent / "croissant.json"
    return mlc.Dataset(croissant_path)


def create_transforms_table(dataset):
    """Create a rich table showing coordinate transforms.

    Desired table fields:
    - transform id
    - name
    - description
    - # of input dimensions
    - # of output dimensions
    - transform type
    """
    table = Table(
        title="Coordinate Transforms", show_header=True, header_style="bold magenta"
    )

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    # table.add_column("Type", style="yellow", justify="center")
    # table.add_column("Dims", style="blue", justify="center")
    # table.add_column("Description", style="white")

    # Extract records from the coordinate_transforms recordset
    for record in dataset.records("table0"):
        transform_id = record["table0/id"].decode()
        name = record["table0/name"].decode()
        table.add_row(transform_id, name)

    return table


def main():
    """Main display function."""
    console = Console()

    try:
        # Load dataset
        console.print(
            "[bold green]Loading coordinate transforms dataset...[/bold green]"
        )
        dataset = load_croissant_dataset()

        # Create and display summary table
        table = create_transforms_table(dataset)
        console.print()
        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise


if __name__ == "__main__":
    main()
