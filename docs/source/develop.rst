Development
===========

Prerequisites
-------------

You need to have the following software properly installed to develop
*MPI for Python*:

* `Python`_ 3.8 or above.

* The `Cython`_ compiler.

* A working `MPI`_ implementation like `MPICH`_ or `Open MPI`_,
  preferably supporting MPI-4 and built with shared/dynamic libraries.

Optionally, consider installing the following packages:

* `NumPy`_ for enabling comprehensive testing of MPI communication.

* `CuPy`_ for enabling comprehensive testing with a GPU-aware MPI.

* `Sphinx`_ to build the documentation.

.. tip::

   Most routine development tasks like building, installing in
   editable mode, testing, and generating documentation can be
   performed with the `spin`_ developer tool. Run :command:`spin` at
   the top level source directory for a list of available subcommands.

.. _Python:    https://www.python.org/
.. _Cython:    https://cython.org/
.. _MPI:       https://www.mpi-forum.org/
.. _MPICH:     https://www.mpich.org/
.. _Open MPI:  https://www.open-mpi.org/
.. _NumPy:     https://numpy.org/
.. _CuPy:      https://cupy.dev/
.. _Sphinx:    https://www.sphinx-doc.org/
.. _spin:      https://github.com/scientific-python/spin


Building
--------

*MPI for Python* uses **setuptools**-based build system that relies on
the :file:`setup.py` file. Some setuptools commands (e.g., *build*)
accept additional options:

.. cmdoption:: --mpi=

   Lets you pass a section with MPI configuration within a special
   configuration file. Alternatively, you can use the :envvar:`MPICFG`
   environment variable.

.. cmdoption:: --mpicc=

   Specify the path or name of the :program:`mpicc` C compiler wrapper.
   Alternatively, use the :envvar:`MPICC` environment variable.

.. cmdoption:: --mpild=

   Specify the full path or name for the MPI-aware C linker.
   Alternatively, use the :envvar:`MPILD` environment variable. If
   not set, the :program:`mpicc` C compiler wrapper is used for
   linking.

.. cmdoption:: --configure

   Runs exhaustive tests for checking about missing MPI types,
   constants, and functions. This option should be passed in order to
   build *MPI for Python* against old MPI-1, MPI-2, or MPI-3
   implementations, possibly providing a subset of MPI-4.

If you use a MPI implementation providing a :program:`mpicc` C
compiler wrapper (e.g., MPICH or Open MPI), it will be used for
compilation and linking. This is the preferred and easiest way to
build *MPI for Python*.

If :program:`mpicc` is found in the executable search path
(:envvar:`PATH` environment variable), simply run the *build*
command::

  $ python setup.py build

If :program:`mpicc` is not in your search path or the compiler wrapper
has a different name, you can run the *build* command specifying its
location, either via the :option:`--mpicc` command option or using the
:envvar:`MPICC` environment variable::

  $ python setup.py build --mpicc=/path/to/mpicc
  $ env MPICC=/path/to/mpicc python setup.py build

Alternatively, you can provide all the relevant information about your
MPI implementation by editing the :file:`mpi.cfg` file located in the
top level source directory. You can use the default section ``[mpi]``
or add a new custom section, for example ``[vendor_mpi]`` (see the
examples provided in the :file:`mpi.cfg` file as a starting point to
write your own section):

.. code-block:: ini

  [mpi]
  include_dirs         = /usr/local/mpi/include
  libraries            = mpi
  library_dirs         = /usr/local/mpi/lib
  runtime_library_dirs = /usr/local/mpi/lib

  [vendor_mpi]
  include_dirs         = /opt/mpi/include ...
  libraries            = mpi ...
  library_dirs         = /opt/mpi/lib ...
  runtime_library_dirs = /opt/mpi/lib ...

  ...

and then run the *build* command specifying you custom
configuration section::

  $ python setup.py build --mpi=vendor_mpi
  $ env MPICFG=vendor_mpi python setup.py build


Installing
----------

*MPI for Python* can be installed in editable mode::

  $ python -m pip install --editable .

After modifying Cython sources, an in-place rebuild is needed::

  $ python setup.py build --inplace


Testing
-------

To quickly test the installation::

  $ mpiexec -n 5 python -m mpi4py.bench helloworld
  Hello, World! I am process 0 of 5 on localhost.
  Hello, World! I am process 1 of 5 on localhost.
  Hello, World! I am process 2 of 5 on localhost.
  Hello, World! I am process 3 of 5 on localhost.
  Hello, World! I am process 4 of 5 on localhost.

  $ mpiexec -n 5 python -m mpi4py.bench ringtest -l 10 -n 1048576
  time for 10 loops = 0.00361614 seconds (5 processes, 1048576 bytes)

If you installed from a git clone or the source distribution, issuing
at the command line::

  $ mpiexec -n 5 python demo/helloworld.py

will launch a five-process run of the Python interpreter and run the
demo script :file:`demo/helloworld.py` from the source distribution.

You can also run all the *unittest* scripts::

  $ mpiexec -n 5 python test/main.py

or, if you have the `pytest`_ unit testing framework installed::

  $ mpiexec -n 5 pytest

.. _pytest: https://docs.pytest.org/
