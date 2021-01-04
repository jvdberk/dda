Digital data tables
===================
Be it (relational) tables, arrays, or just a single number, all the data we work with is just a bunch of numbers somehow collected into an ordered data structure that can be called tabular.
We can call them tensors, sequences, or whatever, the most efficient representation is a flat layout in memory where adjacency also indicates some other ``nearness''.
If we do field work or log our progress on some task, the ordering of time is typically important.
Time is a natural ordering we often encounter as timeseries. of some sort.
Spatially arranged data is another common one.

It is also common for recorded data to be updated.
Sometimes by issuing a correction, but often just by extending the set by adding more values.
For instance, more observations lead to longer time series.
The previous record is usually not invalid, but incomplete with respect to the later date.


The need for descriptive naming
===============================
Changes can render previous data obsolete or they can augment it.
We can therefore recognise two important features for a descriptive naming.
First, versioning to separate the various instances of published data.
Second, a timestamp of last update because the same version can receive updates that supercede previous publications.


File formats
============
HDF5 or json are common and have different focus.
The former tends ti be used for high volume and performannce data storage, while the latter is highly portable and easily be read.


Example
=======

/dda/pi(1).h5

retrieves version 1 at maximal minor and timestamped version of data set pi as an HDF5 file. 
