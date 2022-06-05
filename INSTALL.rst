Using **pip**
-------------

You can install mpi4py from its source distribution using ``pip``::

  $ python -m pip install mpi4py

You can also install the in-development version with::

  $ python -m pip install git+https://github.com/mpi4py/mpi4py

or::

  $ python -m pip install https://github.com/mpi4py/mpi4py/tarball/master

.. note::

   Installing mpi4py from sources requires a C compiler and an MPI
   implementation with development headers and libraries.

.. warning::

   ``pip`` keeps previouly built wheel files on its cache for future
   reuse. If you want to reinstall the ``mpi4py`` package using a
   different or updated MPI implementation, you have to either first
   remove the cached wheel file with::

     $ python -m pip cache remove mpi4py

   or ask ``pip`` to disable the cache::

     $ python -m pip install --no-cache-dir mpi4py


Using **conda**
---------------

The `conda-forge`_ community provides ready-to-use binary packages
from an ever growing collection of software libraries built around the
multi-platform *conda* package manager. Three MPI implementations are
available on conda-forge: Open MPI (Linux and macOS), MPICH (Linux and
macOS), and Microsoft MPI (Windows). You can install mpi4py and your
preferred MPI implementation using the ``conda`` package manager:

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

.. _conda-forge: https://conda-forge.org/


Linux
-----

On **Fedora Linux** systems (as well as **RHEL** and their derivatives
using the EPEL software repository), you can install binary packages
with the system package manager:

* using ``dnf`` and the ``mpich`` package::

  $ sudo dnf install python3-mpi4py-mpich

* using ``dnf`` and the ``openmpi`` package::

  $ sudo dnf install python3-mpi4py-openmpi

Please remember to load the correct MPI module for your chosen MPI
implementation:

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


macOS
-----

**macOS** users can install mpi4py using the `Homebrew`_ package
manager::

  $ brew install mpi4py

Note that the Homebrew mpi4py package uses Open MPI. Alternatively,
install the ``mpich`` package and next install mpi4py from sources
using ``pip``.

.. _Homebrew: https://brew.sh/


Windows
-------

**Windows** users can install mpi4py from binary wheels hosted on the
Python Package Index (PyPI) using ``pip``::

  $ python -m pip install mpi4py

Windows wheels require a separate, system-wide installation of the
`Microsoft MPI <MSMPI_>`_ runtime package.

.. _MSMPI: https://docs.microsoft.com/message-passing-interface
