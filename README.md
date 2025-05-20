# noid - Nathan's opinionated imaging data library

Hi, I'm Nathan. I have opinions about organizing data, particularly when it
comes to datasets that involve large n-dimensional arrays.

This is mostly an experiment to explore/validate some ideas I have around
recommendations I'd like to make.

The key idea is:

1. A dataset is some collection of files - basically a database. The files are
   well-known file types that act as the "tables".
2. A top-level json file acts as a self-describing human-readable index into
   these files. Importantly it (a) points to which files make up the dataset,
   thereby making the data discoverable, and (b) defines important relations
   between aspects of the files.
3. Zarr is the well-known type for images.
4. Microformats are awesome.
5. There are only so many relations we care about with respect to image data.

## Relations

- [RDF triple](https://www.w3.org/TR/rdf11-concepts/#section-triples)

## Image data
