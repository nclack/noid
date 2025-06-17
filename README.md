# noid - Nathan's opinionated imaging data library

This is an exploratory project to validate ideas and develop some design recommendations around imaging data.
This project explores ideas around standardizing how we describe and relate scientific imaging data.

## Features

- json-schema vocabularies for coordinate spaces and transformations with a 
  little json-ld thrown in for good measure
- Support for common transform types (identity, translation, scale, etc.)
- Exploration of integration with Croissant datasets
- Pydantic models for schema validation

## Documentation

See the `/docs` directory for documentation on the approach and standards.
See the `/schemas` directory for the json-schema vocabularies and specifications.

## Open questions

* How to treat the implicit index of an array vs identified dimensions in the ome-zarr data set, especially when there's a base physical transform?
* How to specify all the stuff I haven't specified yet? channel metadata, time series, bounding boxes, etc.