Installation
============

Requirements
------------

You need to have the following software properly installed in order to
build *MPI for Python*:

* A working MPI distribution, preferably a MPI-2 one built with
  shared/dynamic libraries.

  .. note::

     If you want to build some MPI implementation from sources,
     check the instructions at :ref:`building-mpi` in the appendix.

* A Python 2.4 to 2.7 or 3.0 to 3.3 distribution, with Python
  library preferably built with shared/dynamic libraries.

  .. note::

     **Mac OS X** users employing a Python distribution built
     with **universal binaries** may need to temporarily set the
     environment variables :envvar:`MACOSX_DEPLOYMENT_TARGET`,
     :envvar:`SDKROOT`, and :envvar:`ARCHFLAGS` to appropriate values
     in the shell before trying to build/install *MPI for
     Python*. Check the instructions at :ref:`macosx-universal-sdk` in
     the appendix.

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

*MPI for Python* uses a standard distutils-based buildsystem. However,
some distutils commands (like *build*) have additional options:

* :option:`--mpicc=` : let you specify a special location or name for
  the :program:`mpicc` compiler wrapper.

* :option:`--mpi=` : let you pass a section with MPI configuration
  within a special configuration file.

* :option:`--configure` : runs exhaustive tests for checking about
  missing MPI types/constants/calls. This option should be passed in
  order to build *MPI for Python* against old MPI-1 implementations,
  possibly providing a subset of MPI-2.


Downloading
^^^^^^^^^^^

The *MPI for Python* package is available for download at the project
website generously hosted by Google Code. You can use :program:`curl`
or :program:`wget` to get a release tarball::

    $ curl -O http://mpi4py.googlecode.com/files/mpi4py-X.X.X.tar.gz

    $ wget http://mpi4py.googlecode.com/files/mpi4py-X.X.X.tar.gz


Building
^^^^^^^^

After unpacking the release tarball::

    $ tar -zxf mpi4py-X.X.X.tar.gz
    $ cd mpi4py-X.X.X

the distribution is ready for building.

- If you use a MPI implementation providing a :program:`mpicc`
  compiler wrapper (e.g., MPICH 1/2, Open MPI, LAM), it will be used
  for compilation and linking. This is the preferred and easiest way
  of building *MPI for Python*.

  If :program:`mpicc` is located somewhere in your search path, simply
  run the *build* command::

    $ python setup.py build

  If :program:`mpicc` is not in your search path or the compiler
  wrapper has a different name, you can run the *build* command
  specifying its location::

    $ python setup.py build --mpicc=/where/you/have/mpicc

- Alternatively, you can provide all the relevant information about
  your MPI distribution by editing the file called
  :file:`mpi.cfg`. You can use the default section ``[mpi]`` or add a
  new, custom section, for example ``[my_mpi]`` (see the examples
  provided in the :file:`mpi.cfg` file)::

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


Installing
^^^^^^^^^^

After building, the distribution is ready for install.

If you have root privileges (either by log-in as the root user of by
using :command:`sudo`) and you want to install *MPI for Python* in
your system for all users, just do::

    $ python setup.py install

The previous steps will install the :mod:`mpi4py` package at standard
location :file:`{prefix}/lib/python{X}.{X}/site-packages`.

If you do not have root privileges or you want to install *MPI for
Python* for your private use, you have two options depending on the
target Python version.

* For Python 2.6 and up::

      $ python setup.py install --user

* For Python 2.5 and below (assuming your home directory is available
  through the :envvar:`HOME` environment variable)::

      $ python setup.py install --home=$HOME

  Finally, add :file:`$HOME/lib/python` or :file:`$HOME/lib64/python`
  to your :envvar:`PYTHONPATH` environment variable.


Testing
^^^^^^^

Issuing at the command line::

    $ mpiexec -n 5 python demo/helloworld.py

or (in the case of older MPI-1 implementations)::

    $ mpirun -np 5 python demo/helloworld.py

will launch a five-process run of the Python interpreter and run the
test scripts :file:`demo/helloworld.py`.


You can also run all the *unittest* scripts::

    $ mpiexec -n 5 python test/runtests.py

or, if you have nose_ unit testing framework installed::

    $ mpiexec -n 5 nosetests -w test

.. _nose: http://somethingaboutorange.com/mrl/projects/nose/
