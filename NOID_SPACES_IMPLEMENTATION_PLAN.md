# noid-spaces Implementation Plan

## Overview

This document outlines the implementation plan for the noid-spaces package, following the proven pattern established by noid-transforms. The goal is to create a LinkML-based library for coordinate spaces and dimensions with UDUNITS-2 validation.

## Architecture Pattern Analysis

Based on analysis of noid-transforms, the following pattern should be followed:

### Core Components

1. **LinkML Schema Foundation**
   - Location: `schemas/space/v0.linkml.yaml`
   - Defines CoordinateSpace and Dimension classes
   - Links to external schemas as needed
   - Uses abstract base classes with concrete implementations

2. **Generated + Enhanced Model Pattern**
   - Import LinkML-generated classes from `_out/python/`
   - Create enhanced wrapper classes inheriting from generated classes
   - Add validation, convenience methods, and user-friendly APIs
   - Provide `to_dict()` methods for serialization

3. **Registry-Based Factory Functions**
   - Use `noid-registry` for extensible factory pattern
   - `@register` decorator for automatic registration
   - `from_dict()` and `from_json()` orchestration functions
   - Namespace management via schema references

4. **Build System**
   - `build.py` script for LinkML artifact generation
   - Generates JSON Schema, JSON-LD context, Python classes, docs
   - Validates examples and runs comprehensive testing

## Key Differences from noid-transforms

1. **No serialization.py module** - Rely entirely on noid-registry's `to_jsonld`/`from_jsonld`
2. **UDUNITS-2 validation** - Integration with py_udunits2 library for unit validation
3. **Domain focus** - Coordinate spaces and dimensions instead of transformations

## Package Structure

```
packages/noid-spaces/
├── src/noid_spaces/
│   ├── __init__.py      # Main API exports (imports to_jsonld/from_jsonld from noid-registry)
│   ├── models.py        # Enhanced CoordinateSpace, Dimension classes
│   ├── factory.py       # Registry-based factory functions
│   └── validation.py    # UDUNITS-2 validation using py_udunits2
├── build.py            # LinkML artifact generation
├── pyproject.toml      # Package config with dependencies
├── tests/              # Test suite
└── examples/           # Usage examples
```

## Implementation Todo List

### High Priority (Foundation)
- [ ] Create noid-spaces package structure at `/Users/nclack/src/noid/packages/noid-spaces/`
- [ ] Set up pyproject.toml with dependencies: noid-registry, py_udunits2, linkml, linkml-runtime, pydantic
- [ ] Create LinkML schema at `/Users/nclack/src/noid/schemas/space/v0.linkml.yaml`

### Medium Priority (Core Implementation)
- [ ] Implement enhanced models.py with CoordinateSpace and Dimension classes
- [ ] Create factory.py with registry-based factory functions following noid-transforms pattern
- [ ] Implement validation.py with UDUNITS-2 validation using py_udunits2
- [ ] Create __init__.py with main API exports (import to_jsonld/from_jsonld from noid-registry)
- [ ] Create build.py script for LinkML artifact generation (reference schemas from `/Users/nclack/src/noid/schemas/space/`)

### Low Priority (Testing & Polish)
- [ ] Set up tests directory and basic test structure
- [ ] Create usage examples
- [ ] Add comprehensive validation tests for UDUNITS-2 integration

## Key Requirements from Project Instructions

1. **UDUNITS-2 Validation**: Use py_udunits2 library for validating unit strings (from CLAUDE.md)
2. **Dimension Properties**:
   - name, unit, and type properties
   - type can be "space", "time", or "other"
   - Units for space/time should use UDUNITS-2 terms
   - "index" and "arbitrary" are valid for all types
3. **Transform Integration**: Transforms link to coordinate spaces via "input" and "output" properties

## Dependencies

```toml
dependencies = [
    "linkml>=1.9.2",
    "linkml-runtime>=1.9.2",
    "pydantic>=2.0.0",
    "typing-extensions>=4.0.0",
    "noid-registry",
    "py_udunits2",  # For UDUNITS-2 validation
]
```

## Next Steps

1. Start new Claude Code session from `/Users/nclack/src/noid/` directory
2. Create package structure following the todo list above
3. Focus on LinkML schema design first, then enhanced models with validation
4. Follow noid-transforms patterns but avoid creating unnecessary serialization module

## Notes

- The noid-transforms serialization.py module contains comments indicating it may be redundant
- noid-registry already provides comprehensive JSON-LD functionality
- Focus on domain-specific validation and modeling rather than serialization concerns
