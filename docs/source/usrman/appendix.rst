Appendix
========

.. _python-mpi:

MPI-enabled Python interpreter
------------------------------

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

    $ python2.6-mpi
    Python 2.6 (r26:66714, Jun  8 2009, 16:07:26)
    [GCC 4.4.0 20090506 (Red Hat 4.4.0-4)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import sys
    >>> sys.executable
    '/usr/bin/python2.6-mpi'
    >>>


.. _macosx-universal-sdk:

Mac OS X and Universal/SDK Python builds
----------------------------------------

Mac OS X users employing a Python distribution built with support for
`Universal applications <http://www.apple.com/universal/>`_ could have
trouble building *MPI for Python*, specially if they want to link
against MPI libraries built without such support. Another source of
trouble could be a Python build using a specific *deployment target*
and *cross-development SDK* configuration. Workarounds for such issues
are to temporarily set the environment variables
:envvar:`MACOSX_DEPLOYMENT_TARGET`, :envvar:`SDKROOT` and/or
:envvar:`ARCHFLAGS` to appropriate values in the shell before trying
to build/install *MPI for Python*.

An appropriate value for :envvar:`MACOSX_DEPLOYMENT_TARGET` should be
any greater or equal than the one used to build Python, and less or
equal than your system version. The safest choice for end-users would
be to use the system version (e.g, if you are on *Leopard*, you should
try ``MACOSX_DEPLOYMENT_TARGET=10.5``).

An appropriate value for :envvar:`SDKROOT` is the full path name of
any of the SDK's you have at :file:`/Developer/SDKs` directory (e.g.,
``SDKROOT=/Developer/SDKs/MacOSX10.5.sdk``). The safest choice for
end-users would be the one matching the system version; or
alternatively the root directory (i.e., ``SDKROOT=/``).

Appropriate values for :envvar:`ARCHFLAGS` have the form ``-arch
<value>``, where ``<value>`` should be chosen from the following
table:

====== ==========  =========
  @      Intel      PowerPC
====== ==========  =========
32-bit ``i386``    ``ppc``
64-bit ``x86_64``  ``ppc64``
====== ==========  =========

For example, assuming your Mac is running **Snow Leopard** on a
**64-bit Intel** processor and you want to override the hard-wired
cross-development SDK in Python configuration, you can build and
install *MPI for Python* using any of the alternatives below. Note
that environment variables may need to be passed/set both at the build
and install steps (because :program:`sudo` may not pass environment
variables to subprocesses for security reasons)

* Alternative 1::

    $ env MACOSX_DEPLOYMENT_TARGET=10.6 \
          SDKROOT=/                     \
          ARCHFLAGS='-arch x86_64'      \
          python setup.py build [options]

    $ sudo env MACOSX_DEPLOYMENT_TARGET=10.6 \
               SDKROOT=/                     \
               ARCHFLAGS='-arch x86_64'      \
               python setup.py install [options]

* Alternative 2::

    $ export MACOSX_DEPLOYMENT_TARGET=10.6
    $ export SDKROOT=/
    $ export ARCHFLAGS='-arch x86_64'
    $ python setup.py build [options]

    $ sudo -s # enter interactive shell as root
    $ export MACOSX_DEPLOYMENT_TARGET=10.6
    $ export SDKROOT=/
    $ export ARCHFLAGS='-arch x86_64'
    $ python setup.py install [options]
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
    $ ./configure --enable-shared --prefix=/usr/local/mpich2
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

  .. warning::

     MPICH 1 support for dynamic libraries is not completely
     transparent. Users should set the environment variable
     :envvar:`MPICH_USE_SHLIB` to ``yes`` in order to avoid link
     problems when using the :program:`mpicc` compiler wrapper.
