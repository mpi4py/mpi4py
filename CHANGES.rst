=======================
CHANGES: MPI for Python
=======================

:Author:  Lisandro Dalcin
:Contact: dalcinl@gmail.com


Release 3.1.2 [2021-11-04]
==========================

.. warning:: This is the last release supporting Python 2.

* `mpi4py.futures`: Add `_max_workers` property to `MPIPoolExecutor`.

* `mpi4py.util.dtlib`: Fix computation of alignment for predefined datatypes.

* `mpi4py.util.pkl5`: Fix deadlock when using ``ssend()`` + ``mprobe()``.

* `mpi4py.util.pkl5`: Add environment variable `MPI4PY_PICKLE_THRESHOLD`.

* `mpi4py.rc`: Interpret ``"y"`` and ``"n"`` strings as boolean values.

* Fix/add typemap/typestr for `MPI.WCHAR`/`MPI.COUNT` datatypes.

* Minor fixes and additions to documentation.

* Minor fixes to typing support.

* Support for local version identifier (PEP-440).


Release 3.1.1 [2021-08-14]
==========================

.. warning:: This is the last release supporting Python 2.

* Fix typo in Requires-Python package metadata.

* Regenerate C sources with Cython 0.29.24.


Release 3.1.0 [2021-08-12]
==========================

.. warning:: This is the last release supporting Python 2.

* New features:

  + `mpi4py.util`: New package collecting miscellaneous utilities.

* Enhancements:

  + Add pickle-based ``Request.waitsome()`` and ``Request.testsome()``.

  + Add lowercase methods ``Request.get_status()`` and ``Request.cancel()``.

  + Support for passing Python GPU arrays compliant with the `DLPack`_ data
    interchange mechanism (`link <DIM_>`_) and the ``__cuda_array_interface__``
    (CAI) standard (`link <CAI_>`_) to uppercase methods. This support requires
    that mpi4py is built against `CUDA-aware MPI <CAM_>`_ implementations. This
    feature is currently experimental and subject to future changes.

  + `mpi4py.futures`: Add support for initializers and canceling futures at shutdown.
    Environment variables names now follow the pattern ``MPI4PY_FUTURES_*``, the
    previous ``MPI4PY_*`` names are deprecated.

  + Add type annotations to Cython code. The first line of the docstring of functions
    and methods displays a signature including type annotations.

  + Add companion stub files to support type checkers.

  + Support for weak references.

* Miscellaneous:

  + Add a new mpi4py publication (`link <DOI_>`_) to the citation listing.

.. _DLPack: https://github.com/dmlc/dlpack
.. _DIM: https://data-apis.org/array-api/latest/design_topics/data_interchange.html
.. _CAI: https://numba.readthedocs.io/en/stable/cuda/cuda_array_interface.html
.. _CAM: https://developer.nvidia.com/blog/introduction-cuda-aware-mpi/
.. _DOI: https://doi.org/10.1109/MCSE.2021.3083216


Release 3.0.3 [2019-11-04]
==========================

* Regenerate Cython wrappers to support Python 3.8.


Release 3.0.2 [2019-06-11]
==========================

* Bug fixes:

  + Fix handling of readonly buffers in support for Python 2 legacy
    buffer interface. The issue triggers only when using a buffer-like
    object that is readonly and does not export the new Python 3
    buffer interface.
  + Fix build issues with Open MPI 4.0.x series related to removal of
    many MPI-1 symbols deprecated in MPI-2 and removed in MPI-3.
  + Minor documentation fixes.


Release 3.0.1 [2019-02-15]
==========================

* Bug fixes:

  + Fix ``Comm.scatter()`` and other collectives corrupting input send
    list. Add safety measures to prevent related issues in global
    reduction operations.
  + Fix error-checking code for counts in ``Op.Reduce_local()``.

* Enhancements:

  + Map size-specific Python/NumPy typecodes to MPI datatypes.
  + Allow partial specification of target list/tuple arguments in the
    various ``Win`` RMA methods.
  + Workaround for removal of ``MPI_{LB|UB}`` in Open MPI 4.0.
  + Support for Microsoft MPI v10.0.


Release 3.0.0 [2017-11-08]
==========================

* New features:

  + `mpi4py.futures`: Execute computations asynchronously using a pool
    of MPI processes. This package is based on ``concurrent.futures``
    from the Python standard library.
  + `mpi4py.run`: Run Python code and abort execution in case of
    unhandled exceptions to prevent deadlocks.
  + `mpi4py.bench`: Run basic MPI benchmarks and tests.

* Enhancements:

  + Lowercase, pickle-based collective communication calls are now
    thread-safe through the use of fine-grained locking.
  + The ``MPI`` module now exposes a ``memory`` type which is a
    lightweight variant of the builtin ``memoryview`` type, but
    exposes both the legacy Python 2 and the modern Python 3 buffer
    interface under a Python 2 runtime.
  + The ``MPI.Comm.Alltoallw()`` method now uses ``count=1`` and
    ``displ=0`` as defaults, assuming that messages are specified
    through user-defined datatypes.
  + The ``Request.Wait[all]()`` methods now return ``True`` to match
    the interface of ``Request.Test[all]()``.
  + The ``Win`` class now implements the Python buffer interface.

* Backward-incompatible changes:

  + The ``buf`` argument of the ``MPI.Comm.recv()`` method is
    deprecated, passing anything but ``None`` emits a warning.
  + The ``MPI.Win.memory`` property was removed, use the
    ``MPI.Win.tomemory()`` method instead.
  + Executing ``python -m mpi4py`` in the command line is now
    equivalent to ``python -m mpi4py.run``. For the former behavior,
    use ``python -m mpi4py.bench``.
  + Python 2.6 and 3.2 are no longer supported. The ``mpi4py.MPI``
    module may still build and partially work, but other pure-Python
    modules under the ``mpi4py`` namespace will not.
  + Windows: Remove support for legacy MPICH2, Open MPI, and DeinoMPI.


Release 2.0.0 [2015-10-18]
==========================

* Support for MPI-3 features.

  + Matched probes and receives.
  + Nonblocking collectives.
  + Neighborhood collectives.
  + New communicator constructors.
  + Request-based RMA operations.
  + New RMA communication and synchronisation calls.
  + New window constructors.
  + New datatype constructor.
  + New C++ boolean and floating complex datatypes.

* Support for MPI-2 features not included in previous releases.

  + Generalized All-to-All collective (``Comm.Alltoallw()``)
  + User-defined data representations (``Register_datarep()``)

* New scalable implementation of reduction operations for Python
  objects. This code is based on binomial tree algorithms using
  point-to-point communication and duplicated communicator
  contexts. To disable this feature, use
  ``mpi4py.rc.fast_reduce = False``.

* Backward-incompatible changes:

  + Python 2.4, 2.5, 3.0 and 3.1 are no longer supported.
  + Default MPI error handling policies are overriden. After import,
    mpi4py sets the ``ERRORS_RETURN`` error handler in ``COMM_SELF``
    and ``COMM_WORLD``, as well as any new ``Comm``, ``Win``, or
    ``File`` instance created through mpi4py, thus effectively
    ignoring the MPI rules about error handler inheritance.  This way,
    MPI errors translate to Python exceptions.  To disable this
    behavior and use the standard MPI error handling rules, use
    ``mpi4py.rc.errors = 'default'``.
  + Change signature of all send methods,
    ``dest`` is a required argument.
  + Change signature of all receive and probe methods,
    ``source`` defaults to ``ANY_SOURCE``,
    ``tag`` defaults to ``ANY_TAG``.
  + Change signature of send lowercase-spelling methods,
    ``obj`` arguments are not mandatory.
  + Change signature of recv lowercase-spelling methods,
    renamed 'obj' arguments to 'buf'.
  + Change ``Request.Waitsome()`` and ``Request.Testsome()``
    to return ``None`` or ``list``.
  + Change signature of all lowercase-spelling collectives,
    ``sendobj`` arguments are now mandatory,
    ``recvobj`` arguments were removed.
  + Reduction operations ``MAXLOC`` and ``MINLOC`` are no longer
    special-cased in lowercase-spelling methods ``Comm.[all]reduce()``
    and ``Comm.[ex]scan()``, the input object must be specified as a
    tuple ``(obj, location)``.
  + Change signature of name publishing functions.
    The new signatures are
    ``Publish_name(service_name, port_name, info=INFO_NULL)`` and
    ``Unpublish_name(service_name, port_name, info=INFO_NULL)```.
  + ``Win`` instances now cache Python objects exposing memory by
    keeping references instead of using MPI attribute caching.
  + Change signature of ``Win.Lock()``.
    The new signature is
    ``Win.Lock(rank, lock_type=LOCK_EXCLUSIVE, assertion=0)``.
  + Move ``Cartcomm.Map()`` to ``Intracomm.Cart_map()``.
  + Move ``Graphcomm.Map()`` to ``Intracomm.Graph_map()``.
  + Remove the ``mpi4py.MPE`` module.
  + Rename the Cython definition file for use with ``cimport``
    statement from ``mpi_c.pxd`` to ``libmpi.pxd``.


Release 1.3.1 [2013-08-07]
==========================

* Regenerate C wrappers with Cython 0.19.1 to support Python 3.3.

* Install ``*.pxd`` files in ``<site-packages>/mpi4py`` to ease the
  support for Cython's ``cimport`` statement in code requiring to
  access mpi4py internals.

* As a side-effect of using Cython 0.19.1, ancient Python 2.3 is no
  longer supported. If you really need it, you can install an older
  Cython and run ``python setup.py build_src --force``.


Release 1.3 [2012-01-20]
========================

* Now ``Comm.recv()`` accept a buffer to receive the message.

* Add ``Comm.irecv()`` and ``Request.{wait|test}[any|all]()``.

* Add ``Intracomm.Spawn_multiple()``.

* Better buffer handling for PEP 3118 and legacy buffer interfaces.

* Add support for attribute attribute caching on communicators,
  datatypes and windows.

* Install MPI-enabled Python interpreter as
  ``<path>/mpi4py/bin/python-mpi``.

* Windows: Support for building with Open MPI.


Release 1.2.2 [2010-09-13]
==========================

* Add ``mpi4py.get_config()`` to retrieve information (compiler
  wrappers, includes, libraries, etc) about the MPI implementation
  employed to build mpi4py.

* Workaround Python libraries with missing GILState-related API calls
  in case of non-threaded Python builds.

* Windows: look for MPICH2, DeinoMPI, Microsoft HPC Pack at their
  default install locations under %ProgramFiles.

* MPE: fix hacks related to old API's, these hacks are broken when MPE
  is built with a MPI implementations other than MPICH2.

* HP-MPI: fix for missing Fortran datatypes, use dlopen() to load the
  MPI shared library before MPI_Init()

* Many distutils-related fixes, cleanup, and enhancements, better
  logics to find MPI compiler wrappers.

* Support for ``pip install mpi4py``.


Release 1.2.1 [2010-02-26]
==========================

* Fix declaration in Cython include file. This declaration, while
  valid for Cython, broke the simple-minded parsing used in
  conf/mpidistutils.py to implement configure-tests for availability
  of MPI symbols.

* Update SWIG support and make it compatible with Python 3. Also
  generate an warning for SWIG < 1.3.28.

* Fix distutils-related issues in Mac OS X. Now ARCHFLAGS environment
  variable is honored of all Python's ``config/Makefile`` variables.

* Fix issues with Open MPI < 1.4.2 releated to error checking and
  ``MPI_XXX_NULL`` handles.


Release 1.2 [2009-12-29]
========================

* Automatic MPI datatype discovery for NumPy arrays and PEP-3118
  buffers. Now buffer-like objects can be messaged directly, it is no
  longer required to explicitly pass a 2/3-list/tuple like ``[data,
  MPI.DOUBLE]``, or ``[data, count, MPI.DOUBLE]``. Only basic types
  are supported, i.e., all C/C99-native signed/unsigned integral types
  and single/double precision real/complex floating types. Many thanks
  to Eilif Muller for the initial feedback.

* Nonblocking send of pickled Python objects. Many thanks to Andreas
  Kloeckner for the initial patch and enlightening discussion about
  this enhancement.

* ``Request`` instances now hold a reference to the Python object
  exposing the buffer involved in point-to-point communication or
  parallel I/O. Many thanks to Andreas Kloeckner for the initial
  feedback.

* Support for logging of user-defined states and events using `MPE
  <http://www.mcs.anl.gov/research/projects/perfvis/>`_. Runtime
  (i.e., without requiring a recompile!)  activation of logging of all
  MPI calls is supported in POSIX platforms implementing ``dlopen()``.

* Support for all the new features in MPI-2.2 (new C99 and F90
  datatypes, distributed graph topology, local reduction operation,
  and other minor enhancements).

* Fix the annoying issues related to Open MPI and Python dynamic
  loading of extension modules in platforms supporting ``dlopen()``.

* Fix SLURM dynamic loading issues on SiCortex. Many thanks to Ian
  Langmore for providing me shell access.


Release 1.1.0 [2009-06-06]
==========================

* Fix bug in ``Comm.Iprobe()`` that caused segfaults as Python C-API
  calls were issued with the GIL released (issue #2).

* Add ``Comm.bsend()`` and ``Comm.ssend()`` for buffered and
  synchronous send semantics when communicating general Python
  objects.

* Now the call ``Info.Get(key)`` return a *single* value (i.e, instead
  of a 2-tuple); this value is ``None`` if ``key`` is not in the
  ``Info`` object, or a string otherwise. Previously, the call
  redundantly returned ``(None, False)`` for missing key-value pairs;
  ``None`` is enough to signal a missing entry.

* Add support for parametrized Fortran datatypes.

* Add support for decoding user-defined datatypes.

* Add support for user-defined reduction operations on memory
  buffers. However, at most 16 user-defined reduction operations
  can be created. Ask the author for more room if you need it.


Release 1.0.0 [2009-03-20]
==========================

This is the fist release of the all-new, Cython-based, implementation
of *MPI for Python*. Unfortunately, this implementation is not
backward-compatible with the previous one. The list below summarizes
the more important changes that can impact user codes.

* Some communication calls had *overloaded* functionality. Now there
  is a clear distinction between communication of general Python
  object with *pickle*, and (fast, near C-speed) communication of
  buffer-like objects (e.g., NumPy arrays).

  - for communicating general Python objects, you have to use
    all-lowercase methods, like ``send()``, ``recv()``, ``bcast()``,
    etc.

  - for communicating array data, you have to use ``Send()``,
    ``Recv()``, ``Bcast()``, etc. methods. Buffer arguments to these
    calls must be explicitly specified by using a 2/3-list/tuple like
    ``[data, MPI.DOUBLE]``, or ``[data, count, MPI.DOUBLE]`` (the
    former one uses the byte-size of ``data`` and the extent of the
    MPI datatype to define the ``count``).

* Indexing a communicator with an integer returned a special object
  associating the communication with a target rank, alleviating you
  from specifying source/destination/root arguments in point-to-point
  and collective communications. This functionality is no longer
  available, expressions like::

     MPI.COMM_WORLD[0].Send(...)
     MPI.COMM_WORLD[0].Recv(...)
     MPI.COMM_WORLD[0].Bcast(...)

  have to be replaced by::

     MPI.COMM_WORLD.Send(..., dest=0)
     MPI.COMM_WORLD.Recv(..., source=0)
     MPI.COMM_WORLD.Bcast(..., root=0)

* Automatic MPI initialization (i.e., at import time) requests the
  maximum level of MPI thread support (i.e., it is done by calling
  ``MPI_Init_thread()`` and passing ``MPI_THREAD_MULTIPLE``). In case
  you need to change this behavior, you can tweak the contents of the
  ``mpi4py.rc`` module.

* In order to obtain the values of predefined attributes attached to
  the world communicator, now you have to use the ``Get_attr()``
  method on the ``MPI.COMM_WORLD`` instance::

     tag_ub = MPI.COMM_WORLD.Get_attr(MPI.TAG_UB)

* In the previous implementation, ``MPI.COMM_WORLD`` and
  ``MPI.COMM_SELF`` were associated to **duplicates** of the (C-level)
  ``MPI_COMM_WORLD`` and ``MPI_COMM_SELF`` predefined communicator
  handles. Now this is no longer the case, ``MPI.COMM_WORLD`` and
  ``MPI.COMM_SELF`` proxies the **actual** ``MPI_COMM_WORLD`` and
  ``MPI_COMM_SELF`` handles.

* Convenience aliases ``MPI.WORLD`` and ``MPI.SELF`` were removed. Use
  instead ``MPI.COMM_WORLD`` and ``MPI.COMM_SELF``.

* Convenience constants ``MPI.WORLD_SIZE`` and ``MPI.WORLD_RANK`` were
  removed. Use instead ``MPI.COMM_WORLD.Get_size()`` and
  ``MPI.COMM_WORLD.Get_rank()``.
