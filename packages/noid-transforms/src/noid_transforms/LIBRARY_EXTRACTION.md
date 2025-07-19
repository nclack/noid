# Library Extraction Guide

The registry system implemented in this module is designed to be schema-agnostic and extractable as a standalone library. Here's how to extract the generic components:

## Generic Components (Library-Extractable)

These modules contain no transforms-specific logic and can be moved to a standalone library:

### Core Registry System
- `registry.py` - Core registry infrastructure with IRI→factory mapping and collision detection
- `adapter.py` - PyLD data normalization adapter
- `abbreviation.py` - Namespace abbreviation system
- `jsonld_processing.py` - Enhanced JSON-LD processing with PyLD integration

### Dependencies
The extractable library would need these dependencies:
```toml
dependencies = [
    "pyld>=2.0.0",
    "typing-extensions>=4.0.0",
]
```

## Schema-Specific Components (Stay with NOID Transforms)

These modules contain transforms-specific logic:

- `factories.py` - Registry-based factory functions for transforms
- `models.py` - Transform model classes
- `factory.py` - Legacy factory functions and integration layer
- `serialization.py` - Schema-specific serialization
- `validation.py` - Transform validation logic

## Extraction Steps

### 1. Create New Library Structure
```
jsonld_registry/
  __init__.py
  registry.py          # Move from noid_transforms/registry.py
  adapter.py           # Move from noid_transforms/adapter.py
  abbreviation.py      # Move from noid_transforms/abbreviation.py
  jsonld_processing.py # Move from noid_transforms/jsonld_processing.py
```

### 2. Update Imports
In the new library, update imports to be internal:
```python
# In jsonld_registry/jsonld_processing.py
from .registry import registry, UnknownTransformError
from .adapter import PyLDDataAdapter
# etc.
```

### 3. Update NOID Transforms to Use Library
```python
# In noid_transforms/__init__.py
from jsonld_registry import (
    registry, register, set_namespace,
    PyLDDataAdapter, NamespaceAbbreviator,
    from_jsonld as enhanced_from_jsonld,
    to_jsonld as enhanced_to_jsonld
)
```

### 4. Update Dependencies
```toml
# In noid_transforms/pyproject.toml
dependencies = [
    "jsonld-registry>=1.0.0",  # The extracted library
    "linkml>=1.9.2",
    # ... other existing dependencies
]
```

## Public API of Extracted Library

The extracted library would expose:

```python
# Core registry
from jsonld_registry import registry, register, set_namespace

# PyLD processing
from jsonld_registry import from_jsonld, to_jsonld
from jsonld_registry import PyLDDataAdapter

# Namespace abbreviation
from jsonld_registry import NamespaceAbbreviator, create_abbreviator_for_namespaces

# Error types
from jsonld_registry import RegistryError, UnknownTransformError, FactoryValidationError
```

## Usage Example with Extracted Library

```python
import jsonld_registry

# Set namespace for a schema
jsonld_registry.set_namespace("https://example.com/schemas/")

# Register factory functions following supported patterns
@jsonld_registry.register
def my_transform(data: List[float]) -> MyTransform:
    """Single parameter - works with direct values."""
    return MyTransform(data=data)

@jsonld_registry.register
def my_complex_transform(path: str, mode: str = "default") -> MyTransform:
    """Multi-parameter - works with dict input via kwargs expansion."""
    return MyTransform(path=path, mode=mode)

# Process JSON-LD with automatic dispatch
result = jsonld_registry.from_jsonld({
    "@context": {"ex": "https://example.com/schemas/"},
    "ex:my_transform": [1, 2, 3],  # Direct value → my_transform([1, 2, 3])
    "ex:my_complex_transform": {   # Dict → my_complex_transform(path="...", mode="...")
        "path": "data.json",
        "mode": "fast"
    }
})

# Serialize back to JSON-LD
output = jsonld_registry.to_jsonld(result)
```

## Factory Function Design Guidelines

When using the extracted library, factory functions must follow these patterns:

1. **✅ Single parameter**: `def func(data: Type) -> Result`
2. **✅ Multiple named parameters**: `def func(param1: Type, param2: Type = default) -> Result`
3. **✅ No parameters**: `def func() -> Result`
4. **❌ Single dict parameter**: `def func(config: dict) -> Result` (conflicts with kwargs expansion)

## Design Notes

- **Simplified Namespace Management**: Uses global namespace context, no manual prefix management
- **Automatic Prefix Generation**: Prefixes for JSON-LD serialization are generated automatically by the abbreviation system when needed
- **Collision Detection**: Prevents duplicate IRI registrations to catch configuration errors early
- **Per-Registry Isolation**: Different registry instances can register the same IRIs independently
- **Clean Error Messages**: Provides helpful suggestions for typos and lists available options

## Benefits of Extraction

1. **Reusability**: Other projects can use the same registry pattern
2. **Maintainability**: Generic logic separated from schema-specific code
3. **Testing**: Library components can be tested independently
4. **Documentation**: Clear boundaries between generic and specific functionality
5. **Performance**: Library can be optimized independently
6. **Simplicity**: No complex thread-local storage, just straightforward global state
