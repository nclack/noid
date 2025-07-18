# Devlog

## 2025-07-18

Reviewing the generated code. Finishing up transforms.

## 2025-07-16

Changing things to linkml and refactoring to a library per schema.

Exploring namespaced key dispatching of value types.

[calamus] looks nice but I can't quite get it to work and I'm not sure
how to connect it to [linkml].

Maybe [pyld] is better.

I can't quite tell how much is lost in the [linkml] to [jsonld] conversion.

Created a registry system that can be used to invoke
factory functions based on the name of the key. Using
pyld, this enables a from_jsonld that should just 
work for any schema with registered transforms.

### References

- [linkML][linkml] is a flexible modeling language that allows you to author schemas in YAML that describe the structure of your data. 
- [calamus]: A JSON-LD Serialization Libary for Python 

[pyld]: https://github.com/digitalbazaar/pyld
[jsonld]: https://json-ld.org/
[linkml]: https://github.com/linkml/linkml
[calamus]: https://github.com/SwissDataScienceCenter/calamus

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
