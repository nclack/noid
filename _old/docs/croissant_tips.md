# Croissant Tips

## Impressions

The best part of croissant is the `distribution`. `RecordSet` is the next best
part, but it looks very limited and may be unusable. `RecordSet` provides a
way of describing views of the data referenced in the distribution. These views
are intended to provide samples to e.g. pytorch data loaders, and for feeding
[dataset viewers](https://huggingface.co/docs/dataset-viewer/en/index).

We're trying to do something slightly different, which is to model all the
related data in a dataset. There might be several different kinds of tabular
views you can create from a dataset.

We could choose to provide a few standard `RecordSets` but there's not much
value in that. Instead it would be nice if there were clear recipes for doing
so based on the data model.

If we're not using `RecordSets` then maybe it's not worth using croissant.
I would need to make something to act like `distribution`. Together with
`FileObject`, `FileSet` and the `extract` functionality to create id's,
croissant's `distribution` is pretty powerful.

## Looks like Arrays might be coming in 1.1?

See the merged [PR](https://github.com/mlcommons/croissant/pull/807/files)

## Erata

- The "transform" step does not have a "jsonQuery" field as suggested in the
  online spec. It's "jsonPath".

- For "extract" jsonPath expressions don't support "length()" or "size()". It's
  a pretty limited subset of jsonpath implemented by `jsonpath_rw`.

## Problems

- The state of `mlcroissant` is not quite up to implementing all the features mentioned
  in the croissant 1.0 spec. For example, I'm not sure "repeated" fields really work or
  "subField". This is mostly an impression I get from looking at the issue list. But
  also I can't figure repeated fields out; I'm confused.

- Json-valued data for a field looks unsupported. There's also no way to
  transform json values to strings. If there were, I could easily use the
  type of a field to parse a json string that I extract. But this looks to be
  impossible which is fr:reustrating.


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
