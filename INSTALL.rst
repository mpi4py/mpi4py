Using **pip**
-------------

Installing from wheels
~~~~~~~~~~~~~~~~~~~~~~

The mpi4py project builds and publishes binary wheels able to run in a
variety of:

- operating systems: *Linux*, *macOS*, *Windows*;
- processor architectures: *AMD64*, *ARM64*;
- MPI implementations: *MPICH*, *Open MPI*,
  *MVAPICH*, *Intel MPI*, *HPE Cray MPICH*, *Microsoft MPI*.

.. _MPICH:          https://mpich.org
.. _Open MPI:       https://open-mpi.org
.. _MVAPICH:        https://mvapich.cse.ohio-state.edu
.. _HPE Cray MPICH: https://cpe.ext.hpe.com/docs/latest/mpt/mpich/
.. _Intel MPI:      https://software.intel.com/intel-mpi-library
.. _Microsoft MPI:  https://learn.microsoft.com/message-passing-interface/microsoft-mpi

These mpi4py wheels are distributed via the Python Package Index
(`PyPI <https://pypi.org/project/mpi4py/>`_) and can be installed
using `pip`_::

  python -m pip install mpi4py

The mpi4py wheels can be installed in standard Python virtual
environments. The MPI runtime can be provided by other wheels
installed in the same virtual environment.

.. tip::

   `Intel MPI`_ distributes `Linux and Windows wheels
   <impi-rt-wheels_>`_ for Intel-based processor architectures
   (``x86_64``/``AMD64``). mpi4py and Intel MPI wheels can be
   installed side by side to get a ready-to-use Python+MPI
   environment::

      python -m pip install mpi4py impi-rt

   .. _impi-rt-wheels: https://pypi.org/project/impi-rt/#files

The mpi4py wheels can also be installed (with `pip`_) in `conda`_
environments and they should work out of the box, for any MPI package
provided by `conda-forge`_ , and without any special tweak to
environment variables.

.. _pip:   https://pip.pypa.io
.. _conda: https://docs.conda.io

Externally-provided MPI implementations may come from the system
package manager, sysadmin-maintained builds accessible via module
files, or customized user builds. Such usage is supported and
encouraged. However, there are a few platform-specific consideration
to take into account.

Linux (``x86_64``, ``aarch64``)
+++++++++++++++++++++++++++++++

The Linux wheels require

- `MPICH`_ or any other ABI-compatible derivative,
  like `MVAPICH`_, `Intel MPI`_, `HPE Cray MPICH`_.

- `Open MPI`_ or any other ABI-compatible derivative.

Users may need to set the ``LD_LIBRARY_PATH`` environment variable such
that the dynamic linker is able to find at runtime the MPI shared
library file (``libmpi.so.??``).

Debian/Ubuntu
*************

On Debian/Ubuntu systems, Open MPI is the default MPI implementation and
most of the MPI-based applications and libraries provided by the
distribution depend on Open MPI. Nonetheless, MPICH is also available to
users for installation.

In Ubuntu 22.04 and older, due to legacy reasons, the MPICH ABI is
slightly broken: the MPI shared library file is named ``libmpich.so.12``
instead of ``libmpi.so.12`` as required by the `MPICH ABI Compatibility
Initiative <https://www.mpich.org/abi/>`__.

Users without ``sudo`` access can workaround this issue creating a
symbolic link anywhere in their home directory and appending to
``LD_LIBRARY_PATH``.

.. code:: sh

   mkdir -p ~/.local/lib
   multiarch=$(arch)-linux-gnu
   ln -s /usr/lib/$multiarch/libmpich.so.12 ~/.local/lib/libmpi.so.12
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:~/.local/lib

A system-wide fix for all users requires ``sudo`` access:

.. code:: sh

   multiarch=$(arch)-linux-gnu
   sudo ln -sr /usr/lib/$multiarch/libmpi{ch,}.so.12

Fedora/RHEL
***********

On Fedora/RHEL systems, both MPICH and Open MPI are available for
installation. There is no default or preferred MPI implementation.
Instead, users must select their favorite MPI implementation by
loading the proper MPI module.

.. code:: sh

   module load mpi/mpich-$(arch)    # for MPICH
   module load mpi/openmpi-$(arch)  # for Open MPI

After loading the requested MPI module, the ``LD_LIBRARY_PATH``
environment variable should be properly setup.

HPE Cray OS
***********

Users must load the ``cray-mpich-abi`` module. For further details,
refer to `man intro_mpi <cray-mpt-mpichabi_>`__.

.. _cray-mpt-mpichabi: https://cpe.ext.hpe.com/docs/latest/mpt/mpich/intro_mpi.html#using-mpich-abi-compatibility


macOS (``x86_64``, ``arm64``)
+++++++++++++++++++++++++++++

The macOS wheels require

- `MPICH`_ or `Open MPI`_ installed (either manually or via a package
  manager) in the standard prefix ``/usr/local``.

- `MPICH`_ or `Open MPI`_ installed via `Homebrew`_ in the default
  prefix ``/opt/homebrew``.

- `MPICH`_ or `Open MPI`_ installed via `MacPorts`_ in the default
  prefix ``/opt/local``.

.. _Homebrew: https://brew.sh/
.. _MacPorts: https://www.macports.org/


Windows (``AMD64``)
+++++++++++++++++++

The Windows wheels require

-  `Intel MPI`_.

-  `Microsoft MPI`_.

User may need to set the ``I_MPI_ROOT`` or ``MSMPI_BIN`` environment
variables such that the MPI dynamic link library (DLL) file
(``impi.dll`` or ``msmpi.dll``) can be found at runtime.


Installing from source
~~~~~~~~~~~~~~~~~~~~~~

Pre-built binary wheels are not always desired or appropriate. For
example, the published mpi4py wheels may not support a non-mainstream
MPI implementation. You can still install the mpi4py from its source
distribution using ``pip``::

  python -m pip install --no-binary=mpi4py mpi4py

You can also install the in-development version with::

  python -m pip install git+https://github.com/mpi4py/mpi4py

or::

  python -m pip install https://github.com/mpi4py/mpi4py/tarball/master

.. note::

   Installing mpi4py from its source distribution (available at PyPI)
   or Git source code repository (available at GitHub) requires a C
   compiler and a working MPI implementation with development headers
   and libraries.

.. warning::

   ``pip`` keeps previously built wheel files on its cache for future
   reuse. If you want to reinstall the ``mpi4py`` package from its source
   distribution using a different or updated MPI implementation, you have
   to either first remove the cached wheel file::

     python -m pip cache remove mpi4py
     python -m pip install --no-binary=mpi4py mpi4py

   or ask ``pip`` to disable the cache::

     python -m pip install --no-cache-dir --no-binary=mpi4py mpi4py


Using **conda**
---------------

The `conda-forge`_ community provides ready-to-use binary packages
from an ever growing collection of software libraries built around the
multi-platform *conda* package manager. Four MPI implementations are
available on conda-forge: Open MPI (Linux and macOS), MPICH (Linux and
macOS), Intel MPI (Linux and Windows) and Microsoft MPI (Windows).
You can install mpi4py and your preferred MPI implementation using the
``conda`` package manager:

* to use MPICH do::

    conda install -c conda-forge mpi4py mpich

* to use Open MPI do::

    conda install -c conda-forge mpi4py openmpi

* to use Intel MPI do::

    conda install -c conda-forge mpi4py impi_rt

* to use Microsoft MPI do::

    conda install -c conda-forge mpi4py msmpi

MPICH and many of its derivatives are ABI-compatible. You can provide
the package specification ``mpich=X.Y.*=external_*`` (where ``X`` and
``Y`` are the major and minor version numbers) to request the conda
package manager to use system-provided MPICH (or derivative)
libraries. Similarly, you can provide the package specification
``openmpi=X.Y.*=external_*`` to use system-provided Open MPI
libraries.

The ``openmpi`` package on conda-forge has built-in CUDA support, but
it is disabled by default. To enable it, follow the instruction
outlined during ``conda install``. Additionally, UCX support is also
available once the ``ucx`` package is installed.

.. warning::

   Binary conda-forge packages are built with a focus on
   compatibility. The MPICH and Open MPI packages are build in a
   constrained environment with relatively dated OS images. Therefore,
   they may lack support for high-performance features like
   cross-memory attach (XPMEM/CMA). In production scenarios, it is
   recommended to use external (either custom-built or system-provided)
   MPI installations. See the relevant conda-forge documentation about
   `using external MPI libraries <cf-mpi-docs_>`_ .

.. _conda-forge: https://conda-forge.org/
.. _cf-mpi-docs: https://conda-forge.org/docs/user/tipsandtricks/#using-external-message-passing-interface-mpi-libraries


Linux
-----

On **Fedora Linux** systems (as well as **RHEL** and their derivatives
using the EPEL software repository), you can install binary packages
with the system package manager:

* using ``dnf`` and the ``mpich`` package::

    sudo dnf install python3-mpi4py-mpich

* using ``dnf`` and the ``openmpi`` package::

    sudo dnf install python3-mpi4py-openmpi

Please remember to load the correct MPI module for your chosen MPI
implementation:

* for the ``mpich`` package do::

    module load mpi/mpich-$(arch)
    python -c "from mpi4py import MPI"

* for the ``openmpi`` package do::

    module load mpi/openmpi-$(arch)
    python -c "from mpi4py import MPI"

On **Ubuntu Linux** and **Debian Linux** systems, binary packages are
available for installation using the system package manager::

  sudo apt install python3-mpi4py

Note that on Ubuntu/Debian systems, the mpi4py package uses Open
MPI. To use MPICH, install the ``libmpich-dev`` and ``python3-dev``
packages (and any other required development tools). Afterwards,
install mpi4py from sources using ``pip``.


macOS
-----

**macOS** users can install mpi4py using the `Homebrew`_ package
manager::

  brew install mpi4py

Note that the Homebrew mpi4py package uses Open MPI. Alternatively,
install the ``mpich`` package and next install mpi4py from sources
using ``pip``.


Windows
-------

**Windows** users can install mpi4py from binary wheels hosted on the
Python Package Index (PyPI) using ``pip``::

  python -m pip install mpi4py

The Windows wheels available on PyPI are specially crafted to work
with either the `Intel MPI`_ or the `Microsoft MPI`_ runtime,
therefore requiring a separate installation of any one of these
packages.

Intel MPI is under active development and supports recent version of
the MPI standard. Intel MPI can be installed with ``pip`` (see the
`impi-rt`_ package on PyPI), being therefore straightforward to get it
up and running within a Python environment. Intel MPI can also be
installed system-wide as part of the Intel HPC Toolkit for Windows or
via standalone online/offline installers.

.. _impi-rt: https://pypi.org/project/impi-rt/
