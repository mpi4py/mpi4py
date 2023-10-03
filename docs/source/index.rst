MPI for Python
==============

.. only:: html or man

   :Author:   Lisandro Dalcin
   :Contact:  dalcinl@gmail.com
   :Date:     |today|

.. topic:: Abstract

   *MPI for Python* provides Python bindings for the *Message Passing
   Interface* (MPI) standard, allowing Python applications to exploit
   multiple processors on workstations, clusters and supercomputers.

   This package builds on the MPI specification and provides an object
   oriented interface resembling the MPI-2 C++ bindings. It supports
   point-to-point (sends, receives) and collective (broadcasts,
   scatters, gathers) communication of any *picklable* Python object,
   as well as efficient communication of Python objects exposing the
   Python buffer interface (e.g. NumPy arrays and builtin
   bytes/array/memoryview objects).

.. toctree::
   :caption: Contents
   :maxdepth: 2

   intro
   overview
   tutorial
   mpi4py
   mpi4py.MPI
   mpi4py.typing
   mpi4py.futures
   mpi4py.util
   mpi4py.run
   mpi4py.bench
   reference
   citation
   install
   develop
   appendix
   license
   changes

.. only:: html and not singlehtml

   * :ref:`genindex`
