Appendix
========

.. _python-mpi:

MPI-enabled Python interpreter
------------------------------

Some MPI-1 implementations (notably, MPICH 1) **do require** the
actual command line arguments to be passed at the time
:cfunc:`MPI_Init()` is called. In this case, you will need to use a
rebuilt, MPI-enabled, Python interpreter binary executable. A basic
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
pure-distutils based support to build and install a MPI-enabled Python
interpreter executable::

    $ cd mpi4py-X.X.X
    $ python setup.py build_exe [--home=$HOME]
    $ [sudo] python setup.py install_exe

After the above steps you should have the re-built interpreter
installed as :file:`{prefix}/bin/python{X}.{X}-mpi`. Assuming that
:file:`{prefix}/bin` in on your :envvar:`PATH`, you should be able to
enter your MPI-enabled Python interactively, for example::

    $ python2.5-mpi
    Python 2.5.2 (r252:60911, Sep 30 2008, 15:41:38)
    [GCC 4.3.2 20080917 (Red Hat 4.3.2-4)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import sys
    >>> sys.executable
    '/usr/bin/python2.5-mpi'
    >>>


.. _macosx-universal-sdk:

Mac OS X and Universal/SDK Python builds
----------------------------------------

Mac OS X users employing a Python distribution built with support for
`Universal applications <http://www.apple.com/universal/>`_ could have
trouble building *MPI for Python*, specially if they want to link
against MPI libraries built without such support. Another source of
trouble could be a Python build using a specific cross-development SDK
configuration. Workarounds for such issues are to temporarily set the
environment variables :envvar:`ARCHFLAGS` and/or :envvar:`SDKROOT`
to appropriate values in the shell before trying to build/install *MPI
for Python*.

Appropriate values for :envvar:`ARCHFLAGS` have the form ``-arch
<value>``, where ``<value>`` should be chosen from the following
table:

====== ==========  =========
  @      Intel      PowerPC
====== ==========  =========
32-bit ``i386``    ``ppc``
64-bit ``x86_64``  ``ppc64``
====== ==========  =========

An appropriate value for :envvar:`SDKROOT` is the full path name of
any of the SDK's you have at :file:`/Developer/SDKs` directory (e.g.,
``SDKROOT=/Developer/SDKs/MacOSX10.5.sdk``). The safest choice would
be the one matching your system version; perhaps it is better to use
the root directory (i.e., ``SDKROOT=/``) or even an empty value (i.e.,
``SDKROOT=''``).

For example, assuming your Mac has a 64-bit Intel processor and you
want to override the hard-wired SDK in the Python configuration, you
can build and install *MPI for Python* using any of the alternatives
below. Note that environment variables should be passed/set both at
the build and install steps (because :program:`sudo` does not pass
environment variables to subprocesses for security reasons)

* Alternative 1::

    $ env ARCHFLAGS='-arch x86_64' SDKROOT=/ python setup.py build [OPTIONS]

    $ sudo env ARCHFLAGS='-arch x86_64' SDKROOT=/ python setup.py install [OPTIONS]

* Alternative 2::

    $ export ARCHFLAGS='-arch x86_64'
    $ export SDKROOT=/
    $ python setup.py build [OPTIONS]

    $ sudo -s # enter interactive shell as root
    $ export ARCHFLAGS='-arch x86_64'
    $ export SDKROOT=/
    $ python setup.py install [OPTIONS]
    $ exit

.. _building-mpi:


Building MPI from sources
-------------------------

In the list below you have some executive instructions for building
some of the open-source MPI implementations out there with support for
shared/dynamic libraries on POSIX environments.

+ *MPICH 2* ::

    $ tar -zxf mpich2-X.X.X.tar.gz
    $ cd mpich2-X.X.X
    $ ./configure --enable-sharedlibs=gcc --prefix=/usr/local/mpich2
    $ make
    $ make install

+ *Open MPI* ::

    $ tar -zxf openmpi-X.X.X tar.gz
    $ cd openmpi-X.X.X
    $ ./configure --prefix=/usr/local/openmpi
    $ make all
    $ make install

+ *LAM/MPI* ::

    $ tar -zxf lam-X.X.X.tar.gz
    $ cd lam-X.X.X
    $ ./configure --enable-shared --prefix=/usr/local/lam
    $ make
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

- *MPICH 2* ::

    MPI_DIR=/usr/local/mpich2
    export LD_LIBRARY_PATH=$MPI_DIR/lib:$LD_LIBRARY_PATH

- *Open MPI* ::

    MPI_DIR=/usr/local/openmpi
    export LD_LIBRARY_PATH=$MPI_DIR/lib:$LD_LIBRARY_PATH

- *LAM/MPI* ::

    MPI_DIR=/usr/local/lam
    export LD_LIBRARY_PATH=$MPI_DIR/lib:$LD_LIBRARY_PATH

- *MPICH 1* ::

    MPI_DIR=/usr/local/mpich1
    export LD_LIBRARY_PATH=$MPI_DIR/lib/shared:$LD_LIBRARY_PATH:
    export MPICH_USE_SHLIB=yes

  .. warning:: MPICH 1 support for dynamic libraries is not completely
     transparent. Users should set the environment variable
     :envvar:`MPICH_USE_SHLIB` to ``yes`` in order to avoid link
     problems when using the :program:`mpicc` compiler wrapper.
