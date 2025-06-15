# Coordinate Spaces and Transforms Design

## Overview

This document captures the design requirements and decisions for modeling coordinate spaces and their relationships to coordinate transformations in the NOID vocabulary system.

## Requirements from CLAUDE.md

### Coordinate Spaces
- Coordinate spaces are collections of dimensions
- Named coordinate spaces can be defined with physical units corresponding to UDUNITS-2 ontology terms (micrometers, seconds, etc.)
- Each dimension has a name and a unit
- Every array has two implicit coordinate spaces: "coordinates" and "values"
- Implicit spaces are referenced by appending `/coordinates` or `/values` to the array id (e.g., `array0/coordinates`, `array1/values`)

### Transforms
- Coordinate transformations are defined as (input space, output space, transform definition) triples
- Use controlled vocabularies for transform definitions
- Should be composable and extensible

### Integration Requirements
- Build on croissant framework
- Use JSON-LD vocabularies and schemas
- Support zarr-based arrays and ome-zarr files
- Enable rich relational metadata

## Transform Vocabulary Requirements (Implemented)

Based on the recently completed transform vocabulary, we established:

### Core Transform Types
1. **identity** - Maps coordinates without modification
2. **translation** - Shifts coordinates by a constant vector  
3. **scale** - Scales coordinates along each axis
4. **mapAxis** - Axis permutations as mapping of axis names
5. **homogeneous** - Matrix-based transformation using homogeneous coordinates (supports both affine and projective)
6. **rotation** - Matrix-based rotation transformation
7. **sequence** - Composition of multiple transforms applied in sequence
8. **displacements** - Vector field-based transformation using displacement maps
9. **coordinates** - Explicit coordinate mapping transformation

### Self-Describing Parameters
- Each transform type uses property names matching the type (e.g., `translation`, `scale`, `matrix`)
- Native JSON arrays for numeric parameters instead of strings
- JSON-LD context enables type inference from property presence
- No explicit "type" field needed

## Coordinate Space Vocabulary Design

### Core Classes

**CoordinateSpace**
- Base class representing a collection of dimensions
- Has name, description, and list of dimensions
- Can reference physical units from UDUNITS-2

**Dimension** 
- Represents a single axis/dimension within a coordinate space
- Properties: name, unit, description
- Unit should reference UDUNITS-2 terms where applicable

**Transform** (links to existing vocabulary)
- Extends existing transform vocabulary
- Add properties for input and output coordinate spaces
- Maintains existing self-describing parameter approach

### Key Relationships

**hasInputSpace / hasOutputSpace**
- Properties linking transforms to their input/output coordinate spaces
- Enables (input space, output space, transform definition) triple pattern

**hasDimension**
- Property linking coordinate spaces to their constituent dimensions
- Ordered list to preserve dimension sequence

**hasUnit**
- Property linking dimensions to UDUNITS-2 unit terms
- Should reference standard unit vocabulary

### Design Decisions

1. **Coordinate spaces as collections of dimensions** ✅
   - Explicit modeling of dimensions with names, units, and types
   - Support for named coordinate spaces with physical units

2. **Link to existing transform vocabulary** ✅  
   - Extend transforms with input/output space properties
   - Maintain existing self-describing parameter approach

3. **Model input/output space relationships** ✅
   - Clear (input, output, transform) triple structure
   - Enable transform composition and validation

4. **Implicit coordinate/values spaces** ✅ **DECIDED: NOT MODELED**
   - Keep implicit spaces as application-level convention
   - Use `{arrayId}/coordinates` and `{arrayId}/values` pattern
   - Avoids vocabulary complexity without losing functionality

## Implementation Decisions

### Property Naming
- Use short, clean property names: `input`/`output`, `dimensions`, `unit`, `name`
- Avoid verbose names like `hasInputSpace`, `hasDimension`

### Dimension Representation  
- `dimensions` property holds JSON array of dimension objects
- Array order preserves dimension sequence (no separate `dimensionOrder` property)
- Each dimension object contains: `name`, `unit`, `type`

### Dimension Types
- **"space"** - Spatial dimensions (x, y, z)
- **"time"** - Temporal dimensions (t)  
- **"other"** - Non-physical dimensions (channels, samples, etc.)

### Unit System
- **Space/time dimensions**: Should use UDUNITS-2 ontology terms (micrometers, seconds, etc.)
- **All dimensions**: Can use "index" or "arbitrary" units for non-physical quantities
- Flexible approach supporting both physical and abstract coordinate systems

## Resolved Questions

### Unit System Integration ✅
- Flexible coupling with UDUNITS-2: required for space/time, optional for others
- Special units "index" and "arbitrary" for non-physical dimensions
- No need for separate unit vocabulary

### Transform Composition ✅
- Composition handled through existing `sequence` transform type
- Input/output space compatibility validation is application-level concern
- Vocabulary provides building blocks, applications implement logic

## Implementation Complete

✅ TTL vocabulary created at `/schemas/coordinate_spaces.ttl`
- CoordinateSpace and Dimension classes
- Short property names: `input`, `output`, `dimensions`, `unit`, `name`, `type`
- JSON array representation for dimensions
- Flexible unit system with UDUNITS-2 integration
- Transform space relationships

## Build Process and Schema Generation

### Architecture Overview

The NOID project follows a **source-of-truth** approach where TTL vocabularies serve as the authoritative schema definitions. All other formats are generated from these TTL files to ensure consistency and avoid duplication.

### Schema Build Pipeline

```
TTL Vocabularies (Source of Truth)
    ↓
JSON-LD Vocabularies (Generated) → Used by Croissant integration
    ↓
SHACL Shapes (Hand-written) → Used for semantic validation
```

#### Build Command
```bash
uv run noid-build-schemas
```

This command:
1. **Converts TTL to JSON-LD**: Uses `rdflib.Graph.serialize()` to convert TTL vocabularies to JSON-LD format for Croissant compatibility
2. **Copies SHACL shapes**: Copies hand-written SHACL validation files to the generated schemas directory

#### Key Files
- **Source TTL**: `/schemas/coordinate_spaces.ttl`, `/schemas/transforms/vocabulary.ttl`
- **Generated JSON-LD**: `/schemas/coordinate_spaces.jsonld`, `/schemas/transforms/vocabulary.jsonld`
- **Hand-written SHACL**: `/schemas/coordinate_spaces_shapes.ttl`, `/schemas/transforms/shapes.ttl`

### SHACL Semantic Validation

#### Validation Strategy

We use **SHACL (Shapes Constraint Language)** for semantic validation rather than JSON Schema because:

1. **Native RDF/JSON-LD support**: SHACL operates directly on RDF graphs, making it ideal for semantic validation
2. **Rich constraint language**: Supports complex validation rules beyond basic type checking
3. **Integration with ontologies**: Can validate against OWL class hierarchies and relationships
4. **Semantic reasoning**: Supports RDFS inference during validation

#### Hand-written vs Generated SHACL

**Decision**: Use hand-written SHACL shapes as source of truth for validation constraints.

**Rationale**:
- Validation requirements are often more specific than what can be automatically derived from TTL
- Hand-written shapes allow for custom validation messages and complex business rules
- Easier to maintain and understand than generated shapes
- Provides explicit documentation of validation requirements

#### SHACL Shape Examples

**Transform Validation** (`/schemas/transforms/shapes.ttl`):
```turtle
# Translation Transform Shape
noid:TranslationShape
    a sh:NodeShape ;
    sh:targetClass noid:translation ;
    rdfs:label "Translation Transform Shape" ;
    sh:property [
        sh:path noid:translation ;
        sh:name "translation vector" ;
        sh:minCount 1 ;
        sh:nodeKind sh:Literal ;
    ] .
```

**Coordinate Space Validation** (`/schemas/coordinate_spaces_shapes.ttl`):
```turtle
# Coordinate Space Shape
noid:CoordinateSpaceShape
    a sh:NodeShape ;
    sh:targetClass noid:CoordinateSpace ;
    sh:property [
        sh:path noid:dimensions ;
        sh:name "dimensions" ;
        sh:minCount 1 ;
        sh:nodeKind sh:BlankNode ;
        sh:node noid:DimensionShape ;
    ] .

# Dimension Shape with unit constraints
noid:DimensionShape
    a sh:NodeShape ;
    sh:property [
        sh:path noid:unit ;
        sh:in ( "micrometer" "millimeter" "meter" "index" "arbitrary" "second" "minute" "hour" "radian" "degree" ) ;
    ] .
```

#### Validation API

The Python validation module (`src/noid/validation.py`) provides:

```python
# Validate transforms
from noid.validation import validate_transforms
errors = validate_transforms("path/to/transform_data.jsonld")

# Validate coordinate spaces  
from noid.validation import validate_coordinate_spaces
errors = validate_coordinate_spaces("path/to/coordinate_space_data.jsonld")

# Generic SHACL validation
from noid.validation import validate_with_shacl
errors = validate_with_shacl(data_file, shapes_file, data_format="json-ld")
```

#### Test Coverage

Comprehensive test suite (`tests/test_validation.py`) covers:
- ✅ Valid transform examples (translation, scale, homogeneous, identity, mapAxis)
- ✅ Invalid transform examples (missing required properties)
- ✅ Valid coordinate space examples (spatial and temporal dimensions)
- ✅ Invalid coordinate space examples (missing dimensions, bad dimension types)
- ✅ Infrastructure testing (file handling, error reporting)

### Croissant Integration

The generated JSON-LD vocabularies enable semantic integration with MLCommons Croissant datasets:

1. **Vocabulary import**: Croissant datasets can reference NOID vocabularies via JSON-LD `@context`
2. **Semantic validation**: Both Croissant validation and SHACL validation can be applied
3. **Rich metadata**: Coordinate spaces and transforms become first-class entities in dataset descriptions

### Development Workflow

1. **Modify TTL vocabularies** when adding new classes or properties
2. **Update SHACL shapes** when adding new validation constraints  
3. **Run build process** to regenerate JSON-LD vocabularies
4. **Run tests** to ensure validation works correctly
5. **Update examples** to demonstrate new functionality

This architecture ensures that the TTL vocabularies remain the authoritative source while enabling flexible validation and integration with the broader semantic web ecosystem.