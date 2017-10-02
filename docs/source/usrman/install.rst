Installation
============

Requirements
------------

You need to have the following software properly installed in order to
build *MPI for Python*:

* A working MPI implementation, preferably supporting MPI-3 and built
  with shared/dynamic libraries.

  .. note::

     If you want to build some MPI implementation from sources,
     check the instructions at :ref:`building-mpi` in the appendix.

* Python 2.7, 3.3 or above.

  .. note::

     Some MPI-1 implementations **do require** the actual
     command line arguments to be passed in :c:func:`MPI_Init()`. In
     this case, you will need to use a rebuilt, MPI-enabled, Python
     interpreter executable. *MPI for Python* has some support for
     alleviating you from this task. Check the instructions at
     :ref:`python-mpi` in the appendix.


Using **pip** or **easy_install**
---------------------------------

If you already have a working MPI (either if you installed it from
sources or by using a pre-built package from your favourite GNU/Linux
distribution) and the :program:`mpicc` compiler wrapper is on your
search path, you can use :program:`pip`::

  $ [sudo] pip install mpi4py

or alternatively *setuptools* :program:`easy_install` (deprecated)::

  $ [sudo] easy_install mpi4py

.. note::

   If the :program:`mpicc` compiler wrapper is not on your
   search path (or if it has a different name) you can use
   :program:`env` to pass the environment variable :envvar:`MPICC`
   providing the full path to the MPI compiler wrapper executable::

     $ [sudo] env MPICC=/path/to/mpicc pip install mpi4py

     $ [sudo] env MPICC=/path/to/mpicc easy_install mpi4py


Using **distutils**
-------------------

The *MPI for Python* package is available for download at the project
website generously hosted by Bitbucket. You can use :program:`curl`
or :program:`wget` to get a release tarball.

* Using :program:`curl`::

    $ curl -O https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-X.Y.tar.gz

* Using :program:`wget`::

    $ wget https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-X.Y.tar.gz

After unpacking the release tarball::

  $ tar -zxf mpi4py-X.Y.tar.gz
  $ cd mpi4py-X.Y

the package is ready for building.

*MPI for Python* uses a standard distutils-based build system. However,
some distutils commands (like *build*) have additional options:

.. cmdoption:: --mpicc=

   Lets you specify a special location or name for the
   :program:`mpicc` compiler wrapper.

.. cmdoption:: --mpi=

   Lets you pass a section with MPI configuration within a special
   configuration file.

.. cmdoption:: --configure

   Runs exhaustive tests for checking about missing MPI types,
   constants, and functions. This option should be passed in order to
   build *MPI for Python* against old MPI-1 or MPI-2 implementations,
   possibly providing a subset of MPI-3.


If you use a MPI implementation providing a :program:`mpicc` compiler
wrapper (e.g., MPICH, Open MPI), it will be used for compilation and
linking. This is the preferred and easiest way of building *MPI for
Python*.

If :program:`mpicc` is located somewhere in your search path, simply
run the *build* command::

  $ python setup.py build

If :program:`mpicc` is not in your search path or the compiler wrapper
has a different name, you can run the *build* command specifying its
location::

  $ python setup.py build --mpicc=/where/you/have/mpicc

Alternatively, you can provide all the relevant information about your
MPI implementation by editing the file called :file:`mpi.cfg`. You can
use the default section ``[mpi]`` or add a new, custom section, for
example ``[other_mpi]`` (see the examples provided in the
:file:`mpi.cfg` file as a starting point to write your own section)::

  [mpi]

  include_dirs         = /usr/local/mpi/include
  libraries            = mpi
  library_dirs         = /usr/local/mpi/lib
  runtime_library_dirs = /usr/local/mpi/lib

  [other_mpi]

  include_dirs         = /opt/mpi/include ...
  libraries            = mpi ...
  library_dirs         = /opt/mpi/lib ...
  runtime_library_dirs = /op/mpi/lib ...

  ...

and then run the *build* command, perhaps specifying you custom
configuration section::

  $ python setup.py build --mpi=other_mpi

After building, the package is ready for install.

If you have root privileges (either by log-in as the root user of by
using :command:`sudo`) and you want to install *MPI for Python* in
your system for all users, just do::

  $ python setup.py install

The previous steps will install the :mod:`mpi4py` package at standard
location :file:`{prefix}/lib/python{X}.{X}/site-packages`.

If you do not have root privileges or you want to install *MPI for
Python* for your private use, just do::

  $ python setup.py install --user


Testing
-------

To quickly test the installation::

  $ mpiexec -n 5 python -m mpi4py.bench helloworld
  Hello, World! I am process 0 of 5 on localhost.
  Hello, World! I am process 1 of 5 on localhost.
  Hello, World! I am process 2 of 5 on localhost.
  Hello, World! I am process 3 of 5 on localhost.
  Hello, World! I am process 4 of 5 on localhost.

If you installed from source, issuing at the command line::

  $ mpiexec -n 5 python demo/helloworld.py

or (in the case of ancient MPI-1 implementations)::

  $ mpirun -np 5 python `pwd`/demo/helloworld.py

will launch a five-process run of the Python interpreter and run the
test script :file:`demo/helloworld.py` from the source distribution.

You can also run all the *unittest* scripts::

  $ mpiexec -n 5 python test/runtests.py

or, if you have nose_ unit testing framework installed::

  $ mpiexec -n 5 nosetests -w test

.. _nose: http://nose.readthedocs.io/

or, if you have `py.test`_ unit testing framework installed::

  $ mpiexec -n 5 py.test test/

.. _py.test: http://docs.pytest.org/
