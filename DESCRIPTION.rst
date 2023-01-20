==============
MPI for Python
==============

This package provides Python bindings for the *Message Passing
Interface* (MPI_) standard. It is implemented on top of the MPI
specification and exposes an API which grounds on the standard MPI-2
C++ bindings.

.. _MPI: https://www.mpi-forum.org

Features
========

This package supports:

* Convenient communication of any *picklable* Python object

  + point-to-point (send & receive)
  + collective (broadcast, scatter & gather, reductions)

* Fast communication of Python object exposing the *Python buffer
  interface* (NumPy arrays, builtin bytes/string/array objects)

  + point-to-point (blocking/nonblocking/persistent send & receive)
  + collective (broadcast, block/vector scatter & gather, reductions)

* Process groups and communication domains

  + Creation of new intra/inter communicators
  + Cartesian & graph topologies

* Parallel input/output:

  + read & write
  + blocking/nonblocking & collective/noncollective
  + individual/shared file pointers & explicit offset

* Dynamic process management

  + spawn & spawn multiple
  + accept/connect
  + name publishing & lookup

* One-sided operations

  + remote memory access (put, get, accumulate)
  + passive target synchronization (start/complete & post/wait)
  + active target synchronization (lock & unlock)


Install
=======

See `INSTALL.rst <INSTALL.rst>`_.

.. include:: INSTALL.rst


Citation
========

If MPI for Python been significant to a project that leads to an
academic publication, please acknowledge that fact by citing the
project.

See `CITATION.rst <CITATION.rst>`_.

.. include:: CITATION.rst
