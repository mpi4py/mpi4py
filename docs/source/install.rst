Installation
============

Build backends
--------------

mpi4py supports three different build backends: `setuptools`_ (default),
`scikit-build-core`_ (`CMake`_-based), and `meson-python`_
(`Meson`_-based). The build backend can be selected by setting the
:envvar:`MPI4PY_BUILD_BACKEND` environment variable.

.. envvar:: MPI4PY_BUILD_BACKEND

  :choices: ``"setuptools"``, ``"scikit-build-core"``, ``"meson-python"``
  :default: ``"setuptools"``

  Request a build backend for building mpi4py from sources.


Using **setuptools**
~~~~~~~~~~~~~~~~~~~~

.. tip::

   Set the :envvar:`MPI4PY_BUILD_BACKEND` environment variable to
   ``"setuptools"`` to use the `setuptools`_ build backend.

.. _setuptools: https://setuptools.pypa.io/

When using the default `setuptools`_ build backend, mpi4py relies on
the legacy Python distutils framework to build C extension modules.
The following environment variables affect the build configuration.

.. envvar:: MPI4PY_BUILD_MPICC

   The :program:`mpicc` compiler wrapper command is searched for in
   the executable search path (:envvar:`PATH` environment variable)
   and used to compile the :mod:`mpi4py.MPI` C extension module.
   Alternatively, use the :envvar:`MPI4PY_BUILD_MPICC` environment
   variable to the full path or command corresponding to the MPI-aware
   C compiler.

.. envvar:: MPI4PY_BUILD_MPILD

   The :program:`mpicc` compiler wrapper command is also used for
   linking the :mod:`mpi4py.MPI` C extension module.
   Alternatively, use the :envvar:`MPI4PY_BUILD_MPILD` environment
   variable to specify the full path or command corresponding to the
   MPI-aware C linker.

.. envvar:: MPI4PY_BUILD_MPICFG

   If the MPI implementation does not provide a compiler wrapper, or
   it is not installed in a default system location, all relevant
   build information like include/library locations and library lists
   can be provided in an ini-style configuration file under a
   ``[mpi]`` section. mpi4py can then be asked to use the custom build
   information by setting the :envvar:`MPI4PY_BUILD_MPICFG`
   environment variable to the full path of the configuration file. As
   an example, see the :file:`mpi.cfg` file located in the top level
   mpi4py source directory.

.. envvar:: MPI4PY_BUILD_CONFIGURE

   Some vendor MPI implementations may not provide complete coverage
   of the MPI standard, or may provide partial features of newer MPI
   standard versions while advertising support for an older version.
   Setting the :envvar:`MPI4PY_BUILD_CONFIGURE` environment variable
   to a non-empty string will trigger the run of exhaustive checks for
   the availability of all MPI constants, predefined handles, and
   routines.

.. envvar:: MPI4PY_BUILD_MPIABI

   Setting the :envvar:`MPI4PY_BUILD_MPIABI` environment variable to
   ``"1"`` enables enhanced support for the MPI 5.0 standard ABI and
   the MPICH or Open MPI legacy ABIs. The :mod:`mpi4py.MPI` extension
   module is then able to dynamically link at runtime with older
   versions (down to the MPI 3.0 standard) of the corresponding MPI
   implementation used at compile time. This feature is only available
   on Linux, macOS, and Windows. POSIX-like systems other than Linux
   and macOS are not currently supported, although they could easily
   be: all what is needed is for the platform to either support weak
   symbols in shared modules/libraries, or support the standard POSIX
   :c:func:`dlopen`/:c:func:`dlsym` APIs.

.. envvar:: MPI4PY_BUILD_PYSABI

   Build with the CPython 3.10+ :ref:`Stable ABI <python:stable-abi>`.
   Setting the :envvar:`MPI4PY_BUILD_PYSABI` environment variable to a
   string ``"{major}.{minor}"`` defines the `Py_LIMITED_API` value to
   use for building extension modules.

The following environment variables are aliases for the ones described
above. Having shorter names, they are convenient for occasional use in
the command line. Its usage is not recommended in automation scenarios
like packaging recipes, deployment scripts, and container image
creation.

.. envvar:: MPICC

   Convenience alias for :envvar:`MPI4PY_BUILD_MPICC`.

.. envvar:: MPILD

   Convenience alias for :envvar:`MPI4PY_BUILD_MPILD`.

.. envvar:: MPICFG

   Convenience alias for :envvar:`MPI4PY_BUILD_MPICFG`.


Using **scikit-build-core**
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tip::

   Set the :envvar:`MPI4PY_BUILD_BACKEND` environment variable to
   ``"scikit-build-core"`` to use the `scikit-build-core`_ build backend.

When using the `scikit-build-core`_ build backend, mpi4py delegates all
of MPI build configuration to `CMake`_'s `FindMPI`_ module. Besides the
obvious advantage of cross-platform support, this delegation to CMake
may be convenient in build environments exposing vendor software
stacks via intricate module systems. Note however that mpi4py will not
be able to look for MPI routines available beyond the MPI standard
version the MPI implementation advertises to support (via the
:c:macro:`MPI_VERSION` and :c:macro:`MPI_SUBVERSION` macro constants
in the :file:`mpi.h` header file), any missing MPI constant or symbol
will prevent a successful build.

.. _CMake: https://cmake.org/
.. _FindMPI: https://cmake.org/cmake/help/latest/module/FindMPI.html
.. _scikit-build-core: https://scikit-build-core.readthedocs.io/


Using **meson-python**
~~~~~~~~~~~~~~~~~~~~~~

.. tip::

   Set the :envvar:`MPI4PY_BUILD_BACKEND` environment variable to
   ``"meson-python"`` to use the `meson-python`_ build backend.

When using the `meson-python`_ build backend, mpi4py delegates build
tasks to the `Meson`_ build system.

.. warning::

   mpi4py support for the `meson-python`_ build backend is
   experimental. For the time being, users must set the :envvar:`CC`
   environment variable to the command or path corresponding to the
   :program:`mpicc` C compiler wrapper.

.. _Meson: https://mesonbuild.com/
.. _meson-python: https://meson-python.readthedocs.io/


.. include:: ../../INSTALL.rst
