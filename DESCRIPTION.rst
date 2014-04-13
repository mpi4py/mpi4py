MPI for Python
==============

This package provides Python bindings for the **Message Passing
Interface** (MPI_) standard. It is implemented on top of the MPI-1/2/3
specification and exposes an API which grounds on the standard MPI-2
C++ bindings.

.. _MPI: http://www.mpi-forum.org/

This package supports:

+ Convenient communication of any *picklable* Python object

  - point-to-point (send & receive)
  - collective (broadcast, scatter & gather, reductions)

+ Fast communication of Python object exposing the *Python buffer
  interface* (NumPy arrays, builtin bytes/string/array objects)

  - point-to-point (blocking/nonbloking/persistent send & receive)
  - collective (broadcast, block/vector scatter & gather, reductions)

+ Process groups and communication domains

  - Creation of new intra/inter communicators
  - Cartesian & graph topologies

+ Parallel input/output:

  - read & write
  - blocking/nonbloking & collective/noncollective
  - individual/shared file pointers & explicit offset

+ Dynamic process management

  - spawn & spawn multiple
  - accept/connect
  - name publishing & lookup

+ One-sided operations

  - remote memory access (put, get, accumulate)
  - passive target syncronization (start/complete & post/wait)
  - active target syncronization (lock & unlock)


Install
-------

If you have a working MPI implementation and the ``mpicc`` compiler
wrapper is on your search path, you can install this package

+ using ``pip``::

  $ pip install mpi4py

+ using ``easy_install`` (deprecated)::

  $ easy_install mpi4py

You can also install the in-development version of mpi4py

+ using ``pip``::

    $ pip install git+https://bitbucket.org/mpi4py/mpi4py

  or::

    $ pip install https://bitbucket.org/mpi4py/mpi4py/get/master.tar.gz

+ using ``easy_install`` (deprecated)::

    $ easy_install git+https://bitbucket.org/mpi4py/mpi4py

  or::

    $ easy_install https://bitbucket.org/mpi4py/mpi4py/get/master.tar.gz
