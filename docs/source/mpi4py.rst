Design and Interface Overview
=============================

MPI for Python provides an object oriented approach to message passing
which grounds on the standard MPI-2 C++ bindings. The interface was
designed with focus in translating MPI syntax and semantics of
standard MPI-2 bindings for C++ to Python. Any user of the standard
C/C++ MPI bindings should be able to use this module without need of
learning a new interface.

Following pyMPI and Pypar approaches, any Python object to be
transmitted is first serialized at sending processes using the
standard Python module ``cPickle``. After that, string data is
communicated (using ``MPI_CHAR`` or ``MPI_BYTE`` datatypes). Finally,
received strings are unpacked and the original objects are restored at
the reciever processes.

The pickling/unpickling appoach can impose important overheads in
memory as well as processor usage, specially in the case of
communication of objects containing big memory buffers, like long
strings or NumPy arrays. In latest releases, MPI for Python was
improved to support direct communication of any object exporting
single-segment buffer interface. This new feature, and the posibility
of constructing user-defined datatypes describing complicated memory
layouts, enables the implementation of many numerical applications
directly in Python with negligible overhead, almost as fast as
compiled C/C++/Fortran codes.



Communicators
-------------

The ``Comm`` class is a base class for the ``Intracomm`` and ``Intercomm``
classes.  The ``Is_inter()`` method (also ``Is_intra()``, nonstandard but
provided for convenience) is defined for communicator objects and can
be used to determine the particular communicator class.

The two predefined MPI intracommunicators instances are available
through ``COMM_WORLD`` and ``COMM_SELF``.

Communicator size and process rank can be respectively obtained with
``Get_size()`` and ``Get_rank()`` methods.

Communicator comparisons can be done with the ``Compare()`` (static)
method of ``Comm`` class, which returns a value in module constants
``IDENT``, ``CONGRUENT``, ``SIMILAR`` or ``UNEQUAL``.

New communicator instances can be obtained with the ``Clone()`` method
of ``Comm`` objects, ``Dup()`` and ``Split()`` methods of both
``Intracomm`` and ``Intercomm`` objects, and ``Create_intercomm()``
and ``Merge()`` methods of ``Intracomm`` and ``Intercomm`` objects
respectively. Set operations with ``Group`` objects like ``Union()``,
``Intersect()`` and ``Difference()`` are fully supported, as well as
the creation of new communicators from groups.

Virtual topologies (``Cartcomm`` and ``Graphcomm`` classes, which are
derived from ``Intracomm`` class) are fully supported. New instances
can be obtained from intracommunicators with factory methods
``Create_cart()`` and ``Create_graph()`` of ``Intracomm`` class.

Point-to-Point Communications
+++++++++++++++++++++++++++++

Methods ``Send()``, ``Recv()`` and ``Sendrecv()`` of the ``Comm``
class provide support for blocking point-to-point communications.

Non-blocking communications are only supported for objects exporting
the single-segment buffer interface. ``Request`` instances are
returned by ``Isend()`` and ``Irecv()`` methods of the ``Comm``
class. Persistent communications are also supported. ``Prequest``
instances are returned by ``Send_init()`` and ``Recv_init()`` methods
of the ``Comm`` class.

Collective Communications
+++++++++++++++++++++++++

Methods ``Bcast()``, ``Scatter()``, ``Gather()``, ``Allgather()`` and
``Alltoall()`` of communicator objects provide support for collective
communications. Global reduction operations ``Reduce()``,
``Allreduce()``, ``Scan()`` and ``Exscan()`` are supported, but they
are naively implemented for reductions of general Python objects.



One-Sided Communications
------------------------

The ``Win`` class provides all the MPI-2 features for one-sided
communications (also known as *remote memory access (RMA)* ). Methods
``Put()``, ``Get()``, and ``Accumulate()`` can be used for remote
writes, reads, and reductions. All synchronization calls (fence,
active target, and lock) are fully supported.

... XXX Write more



Input/Output
------------

The ``File`` class provides all the MPI-2 features for parallel
input/output. All data access operations, for all kind of positioning
(explicit offsets, individual file pointers, and shared file
pointers), synchronism (bloking, nonblocking, and split collective),
and coordination (noncollective and collective) are fully supported.

... XXX Write more


Environmental Management
------------------------

- *Initialization and Exit*

  Module functions ``Init()`` and ``Finalize()`` provide MPI
  initialization and exit respectively. Module functions
  ``Is_initialized()`` and ``Is_finalized()`` provide the respective
  tests for initialization and finalization.

  .. caution:: ``MPI_INIT`` is actually called when you import the
     ``MPI`` module from the ``mpi4py`` package, but only if MPI is
     not already initialized. Calling ``Init()`` is expected generate
     an MPI error.

  .. note:: ``MPI_FINALIZE`` is registered (by using Python C/API
     function ``Py_AtExit()``) for being automatically called when
     Python processes exit, but only if ``mpi4py`` actually
     initialized MPI. Therefore, there is no need to call
     ``Finalize()`` to ensure MPI termination.


- *Implementation Information*

     + The MPI version number can be retrieved from module function
       ``Get_version()``. It returns a two-integer tuple
       ``(version,subversion)``.

     * The ``Get_processor_name()`` function can be used to access the
       processor name.

     + Communicator attributes are not currently supported.

- *Timers*

  MPI timer functionality is available through the ``Wtime()`` and
  ``Wtick()`` functions.

- *Error Handling*

  Error handling functionality is almost completely supported.  Errors
  originated in native MPI calls will throw an instance of the module
  exception class ``Exception``, which derives from standard Python
  exception ``RuntimeError``.

  In order facilitate communicator sharing with other Python modules
  interfacing MPI-based parallel libraries, default MPI error handlers
  ``ERRORS_RETURN``, ``ERRORS_ARE_FATAL`` can be assigned to and
  retrieved from communicators, windows and files with methods
  ``Set_errhandler()`` and ``Get_errhandler()``.

  .. caution:: Importing with ``from mpi4py.MPI import *`` will cause
     a name clashing with standard Python ``Exception`` base class.


Extensions
----------

MPI for Python adds some extensions to the MPI standard. The rationale
is simplified usage and conformance with some Python idioms and
facilities.

... XXX Write me


Documentation
-------------

The standard Python on-line help mechanism will provide information
about module constants, classes and functions using their
documentation strings.
