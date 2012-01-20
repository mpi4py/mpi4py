Design and Interface Overview
=============================

MPI for Python provides an object oriented approach to message passing
which grounds on the standard MPI-2 C++ bindings. The interface was
designed with focus in translating MPI syntax and semantics of
standard MPI-2 bindings for C++ to Python. Any user of the standard
C/C++ MPI bindings should be able to use this module without need of
learning a new interface.

Communicating Python Objects and Array Data
-------------------------------------------

The Python standard library supports different mechanisms for data
persistence. Many of them rely on disk storage, but *pickling* and
*marshaling* can also work with memory buffers.

The :mod:`pickle` (slower, written in pure Python) and :mod:`cPickle`
(faster, written in C) modules provide user-extensible facilities to
serialize generic Python objects using ASCII or binary formats. The
:mod:`marshal` module provides facilities to serialize built-in Python
objects using a binary format specific to Python, but independent of
machine architecture issues.

*MPI for Python* can communicate any built-in or used-defined Python
object taking advantage of the features provided by the mod:`pickle`
module. These facilities will be routinely used to build binary
representations of objects to communicate (at sending processes), and
restoring them back (at receiving processes).

Although simple and general, the serialization approach (i.e.,
*pickling* and *unpickling*) previously discussed imposes important
overheads in memory as well as processor usage, especially in the
scenario of objects with large memory footprints being
communicated. Pickling generic Python objects, ranging from primitive
or container built-in types to user-defined classes, necessarily
requires computer resources.  Processing is also needed for
dispatching the appropriate serialization method (that depends on the
type of the object) and doing the actual packing. Additional memory is
always needed, and if its total amount in not known *a priori*, many
reallocations can occur.  Indeed, in the case of large numeric arrays,
this is certainly unacceptable and precludes communication of objects
occupying half or more of the available memory resources.

*MPI for Python* supports direct communication of any object exporting
the single-segment buffer interface. This interface is a standard
Python mechanism provided by some types (e.g., strings and numeric
arrays), allowing access in the C side to a contiguous memory buffer
(i.e., address and length) containing the relevant data. This feature,
in conjunction with the capability of constructing user-defined MPI
datatypes describing complicated memory layouts, enables the
implementation of many algorithms involving multidimensional numeric
arrays (e.g., image processing, fast Fourier transforms, finite
difference schemes on structured Cartesian grids) directly in Python,
with negligible overhead, and almost as fast as compiled Fortran, C,
or C++ codes.


Communicators
-------------

In *MPI for Python*, :class:`Comm` is the base class of
communicators. The :class:`Intracomm` and :class:`Intercomm` classes
are sublcasses of the :class:`Comm` class.  The :meth:`Is_inter`
method (and :meth:`Is_intra`, provided for convenience, it is not part
of the MPI specification) is defined for communicator objects and can
be used to determine the particular communicator class.

The two predefined intracommunicator instances are available:
:const:`COMM_SELF` and :const:`COMM_WORLD`. From them, new
communicators can be created as needed.

The number of processes in a communicator and the calling process rank
can be respectively obtained with methods :meth:`Get_size` and
:meth:`Get_rank`. The associated process group can be retrieved from a
communicator by calling the :meth:`Get_group` method, which returns an
instance of the :class:`Group` class. Set operations with
:class:`Group` objects like like :meth:`Union`, :meth:`Intersect` and
:meth:`Difference` are fully supported, as well as the creation of new
communicators from these groups using :meth:`Create`.

New communicator instances can be obtained with the :meth:`Clone`
method of :class:`Comm` objects, the :meth:`Dup` and :meth:`Split`
methods of :class:`Intracomm` and :class:`Intercomm` objects, and
methods :meth:`Create_intercomm` and :meth:`Merge` of
:class:`Intracomm` and :class:`Intercomm` objects respectively.

Virtual topologies (:class:`Cartcomm`, :class:`Graphcomm`, and
:class:`Distgraphcomm` classes, being them specializations of
:class:`Intracomm` class) are fully supported. New instances can be
obtained from intracommunicator instances with factory methods
:meth:`Create_cart` and :meth:`Create_graph` of :class:`Intracomm`
class.


Point-to-Point Communications
-----------------------------

Point to point communication is a fundamental capability of message
passing systems. This mechanism enables the transmittal of data
between a pair of processes, one side sending, the other, receiving.

MPI provides a set of *send* and *receive* functions allowing the
communication of *typed* data with an associated *tag*.  The type
information enables the conversion of data representation from one
architecture to another in the case of heterogeneous computing
environments; additionally, it allows the representation of
non-contiguous data layouts and user-defined datatypes, thus avoiding
the overhead of (otherwise unavoidable) packing/unpacking
operations. The tag information allows selectivity of messages at the
receiving end.


Blocking Communications
^^^^^^^^^^^^^^^^^^^^^^^

MPI provides basic send and receive functions that are *blocking*.
These functions block the caller until the data buffers involved in
the communication can be safely reused by the application program.

In *MPI for Python*, the :meth:`Send`, :meth:`Recv` and
:meth:`Sendrecv` methods of communicator objects provide support for
blocking point-to-point communications within :class:`Intracomm` and
:class:`Intercomm` instances. These methods can communicate memory
buffers. The variants :meth:`send`, :meth:`recv` and :meth:`sendrecv`
can communicate generic Python objects.

Nonblocking Communications
^^^^^^^^^^^^^^^^^^^^^^^^^^

On many systems, performance can be significantly increased by
overlapping communication and computation. This is particularly true
on systems where communication can be executed autonomously by an
intelligent, dedicated communication controller.

MPI provides *nonblocking* send and receive functions. They allow the
possible overlap of communication and computation.  Non-blocking
communication always come in two parts: posting functions, which begin
the requested operation; and test-for-completion functions, which
allow to discover whether the requested operation has completed.

In *MPI for Python*, the :meth:`Isend` and :meth:`Irecv` methods of
the :class:`Comm` class initiate a send and receive operation
respectively. These methods return a :class:`Request` instance,
uniquely identifying the started operation.  Its completion can be
managed using the :meth:`Test`, :meth:`Wait`, and :meth:`Cancel`
methods of the :class:`Request` class. The management of
:class:`Request` objects and associated memory buffers involved in
communication requires a careful, rather low-level coordination. Users
must ensure that objects exposing their memory buffers are not
accessed at the Python level while they are involved in nonblocking
message-passing operations.

Persistent Communications
^^^^^^^^^^^^^^^^^^^^^^^^^

Often a communication with the same argument list is repeatedly
executed within an inner loop. In such cases, communication can be
further optimized by using persistent communication, a particular case
of nonblocking communication allowing the reduction of the overhead
between processes and communication controllers. Furthermore , this
kind of optimization can also alleviate the extra call overheads
associated to interpreted, dynamic languages like Python.

In *MPI for Python*, the :meth:`Send_init` and :meth:`Recv_init`
methods of the :class:`Comm` class create a persistent request for a
send and receive operation respectively.  These methods return an
instance of the :class:`Prequest` class, a subclass of the
:class:`Request` class. The actual communication can be effectively
started using the :meth:`Start` method, and its completion can be
managed as previously described.


Collective Communications
--------------------------

Collective communications allow the transmittal of data between
multiple processes of a group simultaneously. The syntax and semantics
of collective functions is consistent with point-to-point
communication. Collective functions communicate *typed* data, but
messages are not paired with an associated *tag*; selectivity of
messages is implied in the calling order. Additionally, collective
functions come in blocking versions only.

The more commonly used collective communication operations are the
following.

* Barrier synchronization across all group members.

* Global communication functions

  + Broadcast data from one member to all members of a group.

  + Gather data from all members to one member of a group.

  + Scatter data from one member to all members of a group.

* Global reduction operations such as sum, maximum, minimum, etc.

*MPI for Python* provides support for almost all collective
calls. Unfortunately, the :meth:`Alltoallw` and :meth:`Reduce_scatter`
methods are curently unimplemented.

In *MPI for Python*, the :meth:`Bcast`, :meth:`Scatter`,
:meth:`Gather`, :meth:`Allgather` and :meth:`Alltoall` methods of
:class:`Comm` instances provide support for collective communications
of memory buffers. The variants :meth:`bcast`, :meth:`scatter`,
:meth:`gather`, :meth:`allgather` and :meth:`alltoall` can communicate
generic Python objects.  The vector variants (which can communicate
different amounts of data to each process) :meth:`Scatterv`,
:meth:`Gatherv`, :meth:`Allgatherv` and :meth:`Alltoallv` are also
supported, they can only communicate objects exposing memory buffers.

Global reduction operations on memory buffers are accessible through
the :meth:`Reduce`, :meth:`Allreduce`, :meth:`Scan` and :meth:`Exscan`
methods. The variants :meth:`reduce`, :meth:`allreduce`, :meth:`scan`
and :meth:`exscan` can communicate generic Python objects; however,
the actual required reduction computations are performed sequentially
at some process. All the predefined (i.e., :const:`SUM`,
:const:`PROD`, :const:`MAX`, etc.)  reduction operations can be
applied.


Dynamic Process Management
--------------------------

In the context of the MPI-1 specification, a parallel application is
static; that is, no processes can be added to or deleted from a
running application after it has been started. Fortunately, this
limitation was addressed in MPI-2. The new specification added a
process management model providing a basic interface between an
application and external resources and process managers.

This MPI-2 extension can be really useful, especially for sequential
applications built on top of parallel modules, or parallel
applications with a client/server model. The MPI-2 process model
provides a mechanism to create new processes and establish
communication between them and the existing MPI application. It also
provides mechanisms to establish communication between two existing
MPI applications, even when one did not *start* the other.

In *MPI for Python*, new independent processes groups can be created
by calling the :meth:`Spawn` method within an intracommunicator (i.e.,
an :class:`Intracomm` instance).  This call returns a new
intercommunicator (i.e., an :class:`Intercomm` instance) at the parent
process group. The child process group can retrieve the matching
intercommunicator by calling the :meth:`Get_parent` (class) method
defined in the :class:`Comm` class. At each side, the new
intercommunicator can be used to perform point to point and collective
communications between the parent and child groups of processes.

Alternatively, disjoint groups of processes can establish
communication using a client/server approach. Any server application
must first call the :func:`Open_port` function to open a *port* and
the :func:`Publish_name` function to publish a provided *service*, and
next call the :meth:`Accept` method within an :class:`Intracomm`
instance.  Any client applications can first find a published
*service* by calling the :func:`Lookup_name` function, which returns
the *port* where a server can be contacted; and next call the
:meth:`Connect` method within an :class:`Intracomm` instance. Both
:meth:`Accept` and :meth:`Connect` methods return an
:class:`Intercomm` instance. When connection between client/server
processes is no longer needed, all of them must cooperatively call the
:meth:`Disconnect` method of the :class:`Comm` class. Additionally,
server applications should release resources by calling the
:func:`Unpublish_name` and :func:`Close_port` functions.


One-Sided Communications
------------------------

One-sided communications (also called *Remote Memory Access*, *RMA*)
supplements the traditional two-sided, send/receive based MPI
communication model with a one-sided, put/get based
interface. One-sided communication that can take advantage of the
capabilities of highly specialized network hardware. Additionally,
this extension lowers latency and software overhead in applications
written using a shared-memory-like paradigm.

The MPI specification revolves around the use of objects called
*windows*; they intuitively specify regions of a process's memory that
have been made available for remote read and write operations.  The
published memory blocks can be accessed through three functions for
put (remote send), get (remote write), and accumulate (remote update
or reduction) data items. A much larger number of functions support
different synchronization styles; the semantics of these
synchronization operations are fairly complex.

In *MPI for Python*, one-sided operations are available by using
instances of the :class:`Win` class. New window objects are
created by calling the :meth:`Create` method at all processes within a
communicator and specifying a memory buffer . When a window instance
is no longer needed, the :meth:`Free` method should be called.

The three one-sided MPI operations for remote write, read and
reduction are available through calling the methods :meth:`Put`,
:meth:`Get()`, and :meth:`Accumulate` respectively within a
:class:`Win` instance.  These methods need an integer rank identifying
the target process and an integer offset relative the base address of
the remote memory block being accessed.

The one-sided operations read, write, and reduction are implicitly
nonblocking, and must be synchronized by using two primary modes.
Active target synchronization requires the origin process to call the
:meth:`Start` and :meth:`Complete` methods at the origin process, and
target process cooperates by calling the :meth:`Post` and :meth:`Wait`
methods. There is also a collective variant provided by the
:meth:`Fence` method. Passive target synchronization is more lenient,
only the origin process calls the :meth:`Lock` and :meth:`Unlock`
methods. Locks are used to protect remote accesses to the locked
remote window and to protect local load/store accesses to a locked
local window.


Parallel Input/Output
---------------------

The POSIX standard provides a model of a widely portable file
system. However, the optimization needed for parallel input/output
cannot be achieved with this generic interface. In order to ensure
efficiency and scalability, the underlying parallel input/output
system must provide a high-level interface supporting partitioning of
file data among processes and a collective interface supporting
complete transfers of global data structures between process memories
and files. Additionally, further efficiencies can be gained via
support for asynchronous input/output, strided accesses to data, and
control over physical file layout on storage devices. This scenario
motivated the inclusion in the MPI-2 standard of a custom interface in
order to support more elaborated parallel input/output operations.

The MPI specification for parallel input/output revolves around the
use objects called *files*. As defined by MPI, files are not just
contiguous byte streams. Instead, they are regarded as ordered
collections of *typed* data items. MPI supports sequential or random
access to any integral set of these items. Furthermore, files are
opened collectively by a group of processes.

The common patterns for accessing a shared file (broadcast, scatter,
gather, reduction) is expressed by using user-defined datatypes.
Compared to the communication patterns of point-to-point and
collective communications, this approach has the advantage of added
flexibility and expressiveness. Data access operations (read and
write) are defined for different kinds of positioning (using explicit
offsets, individual file pointers, and shared file pointers),
coordination (non-collective and collective), and synchronism
(blocking, nonblocking, and split collective with begin/end phases).

In *MPI forPython*, all MPI input/output operations are performed
through instances of the :class:`File` class. File handles are
obtained by calling the :meth:`Open` method at all processes within a
communicator and providing a file name and the intended access mode.
After use, they must be closed by calling the :meth:`Close` method.
Files even can be deleted by calling method :meth:`Delete`.

After creation, files are typically associated with a per-process
*view*. The view defines the current set of data visible and
accessible from an open file as an ordered set of elementary
datatypes. This data layout can be set and queried with the
:meth:`Set_view` and :meth:`Get_view` methods respectively.

Actual input/output operations are achieved by many methods combining
read and write calls with different behavior regarding positioning,
coordination, and synchronism. Summing up, *MPI for Python* provides
the thirty (30) methods defined in MPI-2 for reading from or writing
to files using explicit offsets or file pointers (individual or
shared), in blocking or nonblocking and collective or noncollective
versions.

Environmental Management
------------------------

Initialization and Exit
^^^^^^^^^^^^^^^^^^^^^^^

Module functions :func:`Init` or :func:`Init_thread` and
:func:`Finalize` provide MPI initialization and finalization
respectively. Module functions :func:`Is_initialized()` and
:func:`Is_finalized()` provide the respective tests for initialization
and finalization.

.. caution::

   :c:func:`MPI_Init()` or :c:func:`MPI_Init_thread()` is
   actually called when you import the :mod:`MPI` module from the
   :mod:`mpi4py` package, but only if MPI is not already
   initialized. In such case, calling :func:`Init`/:func:`Init_thread`
   from Python is expected to generate an MPI error, and in turn an
   exception will be raised.

.. note::

   :c:func:`MPI_Finalize()` is registered (by using Python
   C/API function :c:func:`Py_AtExit()`) for being automatically
   called when Python processes exit, but only if :mod:`mpi4py`
   actually initialized Therefore, there is no need to call
   :func:`Finalize()` from Python to ensure MPI finalization.

Implementation Information
^^^^^^^^^^^^^^^^^^^^^^^^^^

+ The MPI version number can be retrieved from module function
  :func:`Get_version`. It returns a two-integer tuple
  ``(version,subversion)``.

* The :func:`Get_processor_name` function can be used to access the
  processor name.

* The values of predefined attributes attached to the world
  communicator can be obtained by calling the :meth:`Get_attr` method
  within the :const:`COMM_WORLD` instance.

Timers
^^^^^^

MPI timer functionalities are available through the :func:`Wtime` and
:func:`Wtick` functions.

Error Handling
^^^^^^^^^^^^^^

Error handling functionality is almost completely supported.  Errors
originated in native MPI calls will raise an instance of the module
exception class :exc:`Exception`, which is a subclass of the standard
Python exception :exc:`RuntimeError`.

.. caution::

   Importing with ``from mpi4py.MPI import *`` will cause
   a name clashing with standard Python :exc:`Exception` base class.

In order facilitate communicator sharing with other Python modules
interfacing MPI-based parallel libraries, default MPI error handlers
:const:`ERRORS_RETURN`, :const:`ERRORS_ARE_FATAL` can be assigned to
and retrieved from communicators, windows and files with methods
:meth:`{Class}.Set_errhandler` and :meth:`{Class}.Get_errhandler`.
