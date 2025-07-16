# Devlog

## 2025-07-08

- [ ] need to rename to something not `noid`

I've created a basic set of schemas covering spatial transforms, coordinate
spaces, and data sources. I've used those to create a data set.

The schema are written in JSON schema and I use those to generate some basic
pydantic models. Those just do some basic validation but another layer would be
required for more complex validation.

I want to make a couple changes though:

1. I want to move to linkml for the schema, and possibly use that to do code
   generation and jsonld generation.
2. I want to think more about how datasets will be appended to over time.
