MPI for Python
==============

This package provides Python bindings for the *Message Passing
Interface* (MPI_) standard. It is implemented on top of the MPI
specification and exposes an API which grounds on the standard MPI-2
C++ bindings.

.. _MPI: https://www.mpi-forum.org

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

You can install mpi4py from its source distribution using ``pip``::

  $ python -m pip install mpi4py

You can also install the in-development version with::

  $ python -m pip install git+https://github.com/mpi4py/mpi4py

or::

  $ python -m pip install https://github.com/mpi4py/mpi4py/tarball/master

Installing from source requires compilers and a working MPI
implementation. The ``mpicc`` compiler wrapper is looked for on the
executable search path (``PATH`` environment variable). Alternatively,
you can set the ``MPICC`` environment variable to the full path or
command corresponding to the MPI-aware C compiler.

The **conda-forge** community provides ready-to-use binary packages
from an ever growing collection of software libraries built around the
multi-platform *conda* package manager. Three MPI implementations are
available on conda-forge: Open MPI (Linux and macOS), MPICH (Linux and
macOS), and Microsoft MPI (Windows). You can install mpi4py and your
preferred MPI implementation using ``conda``::

* to use MPICH do::

  $ conda install -c conda-forge mpi4py mpich

* to use Open MPI do::

  $ conda install -c conda-forge mpi4py openmpi

* to use Microsoft MPI do::

  $ conda install -c conda-forge mpi4py msmpi

MPICH and many of its derivatives are ABI-compatible. You can provide
the package specification ``mpich=X.Y.*=external_*`` (where ``X`` and
``Y`` are the major and minor version numbers) to request the conda
package manager to use system-provided MPICH (or derivative)
libraries.

The ``openmpi`` package on conda-forge has built-in CUDA support, but
it is disabled by default. To enable it, follow the instruction
outlined during ``conda install``. Additionally, UCX support is also
available once the ``ucx`` package is installed.

On **Fedora Linux** systems (as well as **RHEL** and their derivatives
using the EPEL software repository), you can install binary packages
with the system package manager::

* using ``dnf`` and the ``mpich`` package::

  $ sudo dnf install python3-mpi4py-mpich

* using ``dnf`` and the ``openmpi`` package::

  $ sudo dnf install python3-mpi4py-openmpi

Please remember to load the correct MPI module for your chosen MPI
implementation

* for the ``mpich`` package do::

  $ module load mpi/mpich-$(arch)
  $ python -c "from mpi4py import MPI"

* for the ``openmpi`` package do::

  $ module load mpi/openmpi-$(arch)
  $ python -c "from mpi4py import MPI"

On **Ubuntu Linux** and **Debian Linux** systems, binary packages are
available for installation using the system package manager::

  $ sudo apt install python3-mpi4py

Note that on Ubuntu/Debian systems, the mpi4py package uses Open
MPI. To use MPICH, install the ``libmpich-dev`` and ``python3-dev``
packages (and any other required development tools). Afterwards,
install mpi4py from sources using ``pip``.

**macOS** users can install mpi4py using the Homebrew package
manager::

  $ brew install mpi4py

Note that the Homebrew mpi4py package uses Open MPI. Alternatively,
install the ``mpich`` package and next install mpi4py from sources
using ``pip``.

**Windows** users can install mpi4py from binary wheels hosted on the
Python Package Index (PyPI) using ``pip``::

  $ python -m pip install mpi4py

Windows wheels require a separate, system-wide installation of the
Microsoft MPI runtime.


Citations
---------

If MPI for Python been significant to a project that leads to an
academic publication, please acknowledge that fact by citing the
project.

* L. Dalcin and Y.-L. L. Fang,
  *mpi4py: Status Update After 12 Years of Development*,
  Computing in Science & Engineering, 23(4):47-54, 2021.
  https://doi.org/10.1109/MCSE.2021.3083216

* L. Dalcin, P. Kler, R. Paz, and A. Cosimo,
  *Parallel Distributed Computing using Python*,
  Advances in Water Resources, 34(9):1124-1139, 2011.
  https://doi.org/10.1016/j.advwatres.2011.04.013

* L. Dalcin, R. Paz, M. Storti, and J. D'Elia,
  *MPI for Python: performance improvements and MPI-2 extensions*,
  Journal of Parallel and Distributed Computing, 68(5):655-662, 2008.
  https://doi.org/10.1016/j.jpdc.2007.09.005

* L. Dalcin, R. Paz, and M. Storti,
  *MPI for Python*,
  Journal of Parallel and Distributed Computing, 65(9):1108-1115, 2005.
  https://doi.org/10.1016/j.jpdc.2005.03.010
