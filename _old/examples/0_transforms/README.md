# Transform Examples

Demonstrates coordinate transform vocabulary using Croissant dataset format.

## Files

- `transforms.json` - Croissant dataset with transform examples
- `transforms_table.json` - JSON table containing transform definitions
- `display_transforms.py` - Script to display and validate transforms

## Transform Types

Examples include identity, translation, scale, mapAxis, homogeneous
(affine/projective), displacements, and coordinates transforms using
self-describing parameters.

## Usage

```bash
uv run display_transforms.py
```

Validates transforms against JSON schema and displays the RecordSet.
