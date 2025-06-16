# Croissant Tips

## Rules for Making Joins Between RecordSets

When you need to join data from different sources or use different extraction methods on the same file, follow these rules:

### 1. RecordSet IDs are Required
Each RecordSet needs both `@id` and `name` properties with consistent naming:
```json
{
  "@type": "cr:RecordSet",
  "@id": "records0",
  "name": "records0",
  "description": "Transform parameters extracted from JSON"
}
```

### 2. Field Naming Convention
Field `@id` and `name` should follow the pattern `"<recordset_id>/<field_name>"`:
```json
{
  "@type": "cr:Field",
  "@id": "records0/id",
  "name": "records0/id",
  "description": "Transform ID for joining"
}
```

### 3. Join Keys Must Have References
The field that acts as the foreign key needs a `references` object pointing to the primary key field in another recordset:
```json
{
  "@id": "records1/id",
  "source": {
    "fileObject": {"@id": "table"},
    "extract": {"column": "id"}
  },
  "references": {
    "field": {"@id": "records0/id"}
  }
}
```

### 4. Source Field References
When pulling data from another recordset, use the `source.field` syntax:
```json
{
  "@id": "records1/parameters",
  "source": {
    "field": {"@id": "records0/parameters"}
  }
}
```

### 5. Separate RecordSets for Different Extraction Methods
Different extraction methods require separate recordsets. For example:
- RecordSet using column extraction: `"extract": {"column": "id"}`
- RecordSet using JSONPath extraction: `"extract": {"jsonPath": "$.id"}`

### 6. Join Field Must Exist in Both RecordSets
The joining field must be present in both recordsets - one as the primary key and one with the `references` pointing to it.

## Example Use Case
This pattern is useful when you need to:
- Extract different views of the same data using different methods
- Join tabular data (column extraction) with JSON data (JSONPath extraction)
- Maintain referential integrity between related datasets
- Create denormalized recordsets for ML workflows