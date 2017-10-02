Appendix
========

.. _python-mpi:

MPI-enabled Python interpreter
------------------------------

  .. warning::

     These days it is no longer required to use the MPI-enabled Python
     interpreter in most cases, and, therefore, is not built by
     default anymore because it is too difficult to reliably build a
     Python interpreter across different distributions.  If you know
     that you still **really** need it, see below on how to use the
     `build_exe` and `install_exe` commands.

Some MPI-1 implementations (notably, MPICH 1) **do require** the
actual command line arguments to be passed at the time
:c:func:`MPI_Init()` is called. In this case, you will need to use a
re-built, MPI-enabled, Python interpreter binary executable. A basic
implementation (targeting Python 2.X) of what is required is shown
below:

.. sourcecode:: c

    #include <Python.h>
    #include <mpi.h>

    int main(int argc, char *argv[])
    {
       int status, flag;
       MPI_Init(&argc, &argv);
       status = Py_Main(argc, argv);
       MPI_Finalized(&flag);
       if (!flag) MPI_Finalize();
       return status;
    }

The source code above is straightforward; compiling it should also
be. However, the linking step is more tricky: special flags have to be
passed to the linker depending on your platform. In order to alleviate
you for such low-level details, *MPI for Python* provides some
pure-distutils based support to build and install an MPI-enabled
Python interpreter executable::

    $ cd mpi4py-X.X.X
    $ python setup.py build_exe [--mpi=<name>|--mpicc=/path/to/mpicc]
    $ [sudo] python setup.py install_exe [--install-dir=$HOME/bin]

After the above steps you should have the MPI-enabled interpreter
installed as :file:`{prefix}/bin/python{X}.{X}-mpi` (or
:file:`$HOME/bin/python{X}.{X}-mpi`). Assuming that
:file:`{prefix}/bin` (or :file:`$HOME/bin`) is listed on your
:envvar:`PATH`, you should be able to enter your MPI-enabled Python
interactively, for example::

    $ python2.7-mpi
    Python 2.7.8 (default, Nov 10 2014, 08:19:18)
    [GCC 4.9.2 20141101 (Red Hat 4.9.2-1)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import sys
    >>> sys.executable
    '/usr/bin/python2.7-mpi'
    >>>


.. _building-mpi:


Building MPI from sources
-------------------------

In the list below you have some executive instructions for building
some of the open-source MPI implementations out there with support for
shared/dynamic libraries on POSIX environments.

+ *MPICH* ::

    $ tar -zxf mpich-X.X.X.tar.gz
    $ cd mpich-X.X.X
    $ ./configure --enable-shared --prefix=/usr/local/mpich
    $ make
    $ make install

+ *Open MPI* ::

    $ tar -zxf openmpi-X.X.X tar.gz
    $ cd openmpi-X.X.X
    $ ./configure --prefix=/usr/local/openmpi
    $ make all
    $ make install

+ *MPICH 1* ::

    $ tar -zxf mpich-X.X.X.tar.gz
    $ cd mpich-X.X.X
    $ ./configure --enable-sharedlib --prefix=/usr/local/mpich1
    $ make
    $ make install

Perhaps you will need to set the :envvar:`LD_LIBRARY_PATH`
environment variable (using :command:`export`, :command:`setenv` or
what applies to your system) pointing to the directory containing the
MPI libraries . In case of getting runtime linking errors when running
MPI programs, the following lines can be added to the user login shell
script (:file:`.profile`, :file:`.bashrc`, etc.).

- *MPICH* ::

    MPI_DIR=/usr/local/mpich
    export LD_LIBRARY_PATH=$MPI_DIR/lib:$LD_LIBRARY_PATH

- *Open MPI* ::

    MPI_DIR=/usr/local/openmpi
    export LD_LIBRARY_PATH=$MPI_DIR/lib:$LD_LIBRARY_PATH

- *MPICH 1* ::

    MPI_DIR=/usr/local/mpich1
    export LD_LIBRARY_PATH=$MPI_DIR/lib/shared:$LD_LIBRARY_PATH:
    export MPICH_USE_SHLIB=yes

  .. warning::

     MPICH 1 support for dynamic libraries is not completely
     transparent. Users should set the environment variable
     :envvar:`MPICH_USE_SHLIB` to ``yes`` in order to avoid link
     problems when using the :program:`mpicc` compiler wrapper.
