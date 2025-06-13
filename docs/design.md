# Multi-dimensional Array relational model

The aim of this project is to describe datasets that involve a number of
different types of data, including multi-dimensional arrays. These kinds of data
are produced by various scientific instruments, such as telescopes, microscopes,
and particle accelerators. The data can be represented as arrays of arrays,
where each element represents a measurement or observation. The arrays can be
of any dimensionality, from one-dimensional arrays to n-dimensional arrays. For
example, a one-dimensional array might represent a time series of temperature
measurements, while a two-dimensional array might represent a grid of pixel
values from an image. A three-dimensional array might represent a volume of data
from a 3D scanner, and so on. Applications include medical and
scientific imaging, geospatial data, and machine learning.

Bioimaging, in particular, is an evolving field. New experimental pipelines
and approaches demand different ways of organizing data. This project aims to
provide a flexible and scalable data model that can accommodate the diverse
needs of bioimaging researchers.

Internally, we need a standardized way of organizing data so that the data is
easily accessible and reusable. When it comes to data design, it is important
to understand the impact of choices on costs for transforming the data to a
standard, and for maintaining the software for validating the data and making it
accessible to users.

## Data modelling approach

A dataset is a collection of related data of different kinds. It is described by
a schema. The schema defines the structure of the data, including the types of
data, the relationships between the data, and the constraints on the data. The
schema is used to validate the data and to ensure that the data is consistent
and complete. It may also be used to generate code that can be used to
access and manipulate the data.

A schema is composed from vocabularies and ontologies using a particular syntax.
Vocabularies are collections of terms that are used to describe the data.
Ontologies are collections of terms that are used to describe the relationships
between the data.

Here, we're using [json-ld](https://json-ld.org/) to represent the schema and
define vocabularies and ontologies. A strong source of inspiration is [croissant](https://croissant.dev/).
