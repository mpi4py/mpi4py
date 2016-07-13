MPI for Python
==============

This package provides Python bindings for the **Message Passing
Interface** (MPI_) standard. It is implemented on top of the MPI-1/2/3
specification and exposes an API which grounds on the standard MPI-2
C++ bindings.

.. _MPI: http://www.mpi-forum.org/

Features
--------

This package supports:

* Convenient communication of any *picklable* Python object

  + point-to-point (send & receive)
  + collective (broadcast, scatter & gather, reductions)

* Fast communication of Python object exposing the *Python buffer
  interface* (NumPy arrays, builtin bytes/string/array objects)

  + point-to-point (blocking/nonbloking/persistent send & receive)
  + collective (broadcast, block/vector scatter & gather, reductions)

* Process groups and communication domains

  + Creation of new intra/inter communicators
  + Cartesian & graph topologies

* Parallel input/output:

  + read & write
  + blocking/nonbloking & collective/noncollective
  + individual/shared file pointers & explicit offset

* Dynamic process management

  + spawn & spawn multiple
  + accept/connect
  + name publishing & lookup

* One-sided operations

  + remote memory access (put, get, accumulate)
  + passive target syncronization (start/complete & post/wait)
  + active target syncronization (lock & unlock)


Install
-------

Once you have a working MPI implementation and the ``mpicc`` compiler
wrapper is on your search path, you can install this package

* using ``pip``::

  $ pip install mpi4py

* using ``easy_install`` (deprecated)::

  $ easy_install mpi4py

You can also install the in-development version of mpi4py

* using ``pip``::

    $ pip install git+https://bitbucket.org/mpi4py/mpi4py

  or::

    $ pip install https://bitbucket.org/mpi4py/mpi4py/get/master.tar.gz

* using ``easy_install`` (deprecated)::

    $ easy_install git+https://bitbucket.org/mpi4py/mpi4py

  or::

    $ easy_install https://bitbucket.org/mpi4py/mpi4py/get/master.tar.gz

You can also install it directly on Fedora (as well as RHEL and their
derivatives using the EPEL software repository)

* using ``dnf`` and the ``mpich`` package on ``x86_64``::

  $ dnf install mpi4py-mpich

* using ``dnf`` and the ``openmpi`` package on ``x86_64``::

  $ dnf install mpi4py-openmpi

Please remember to load the correct module for your choosen MPI environment

* for ``mpich`` package on ``x86_64`` do::

  $ module load mpi/mpich-x86_64
  $ python -c "import mpi4py"

* for ``openmpi`` package on ``x86_64`` do::

  $ module load mpi/openmpi-x86_64
  $ python -c "import mpi4py"


Citations
---------

If MPI for Python been significant to a project that leads to an
academic publication, please acknowledge that fact by citing the
project.

* L. Dalcin, P. Kler, R. Paz, and A. Cosimo,
  *Parallel Distributed Computing using Python*,
  Advances in Water Resources, 34(9):1124-1139, 2011.
  http://dx.doi.org/10.1016/j.advwatres.2011.04.013

* L. Dalcin, R. Paz, M. Storti, and J. D'Elia,
  *MPI for Python: performance improvements and MPI-2 extensions*,
  Journal of Parallel and Distributed Computing, 68(5):655-662, 2008.
  http://dx.doi.org/10.1016/j.jpdc.2007.09.005

* L. Dalcin, R. Paz, and M. Storti,
  *MPI for Python*,
  Journal of Parallel and Distributed Computing, 65(9):1108-1115, 2005.
  http://dx.doi.org/10.1016/j.jpdc.2005.03.010
