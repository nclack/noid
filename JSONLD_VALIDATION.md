# JSON-LD Validation for NOID Project

This project includes comprehensive JSON-LD validation using a PEP 723-enabled script that automatically manages its dependencies.

## Quick Start

```bash
# Run directly (uses uv run automatically via shebang)
./validate_jsonld.py --all-transforms

# Or explicitly with uv run
uv run validate_jsonld.py --all-transforms

# Validate specific files
./validate_jsonld.py transforms/examples/transforms.jsonld

# Verbose output
./validate_jsonld.py --all-transforms -v
```

## What Gets Validated

The script performs comprehensive JSON-LD validation:

✅ **JSON Syntax** - Basic JSON parsing correctness
✅ **JSON-LD Processing** - Expansion, compaction, and flattening
✅ **Context Resolution** - Namespace and vocabulary validation
✅ **Schema Validation** - Against JSON Schema files (when available)
✅ **Structural Requirements** - Basic JSON-LD structure rules

## Dependencies

The script automatically installs these dependencies when run with `uv run`:
- `pyld>=2.0.0` - JSON-LD processing library
- `jsonschema>=4.0.0` - JSON Schema validation

## Integration

### Test Suite
```bash
uv run python -m pytest tests/test_validation.py -v
```

### Build System
The validation is integrated into `transforms/build.py` and runs automatically during builds.

### Manual Validation in Python
```python
from pyld import jsonld
import json

# Load and validate
with open('transforms/examples/transforms.jsonld', 'r') as f:
    data = json.load(f)

# Test JSON-LD operations
expanded = jsonld.expand(data)
compacted = jsonld.compact(data, data.get("@context", {}))
flattened = jsonld.flatten(data)
```

## Status

Current files validation status:
- ✅ `transforms/examples/transforms.jsonld` - VALID
- ✅ `transforms/examples/sequences.jsonld` - VALID

## Alternative Tools

- **JSON-LD Playground**: https://json-ld.org/playground/
- **MLCroissant validation**: `uv run mlcroissant validate --jsonld <file>`
