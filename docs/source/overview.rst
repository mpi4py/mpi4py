Overview
========

.. currentmodule:: mpi4py.MPI

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

The :mod:`pickle` modules provide user-extensible facilities to
serialize general Python objects using ASCII or binary formats. The
:mod:`marshal` module provides facilities to serialize built-in Python
objects using a binary format specific to Python, but independent of
machine architecture issues.

*MPI for Python* can communicate any built-in or user-defined Python
object taking advantage of the features provided by the :mod:`pickle`
module. These facilities will be routinely used to build binary
representations of objects to communicate (at sending processes), and
restoring them back (at receiving processes).

Although simple and general, the serialization approach (i.e.,
*pickling* and *unpickling*) previously discussed imposes important
overheads in memory as well as processor usage, especially in the
scenario of objects with large memory footprints being
communicated. Pickling general Python objects, ranging from primitive
or container built-in types to user-defined classes, necessarily
requires computer resources.  Processing is also needed for
dispatching the appropriate serialization method (that depends on the
type of the object) and doing the actual packing. Additional memory is
always needed, and if its total amount is not known *a priori*, many
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

In *MPI for Python*, `Comm` is the base class of communicators. The
`Intracomm` and `Intercomm` classes are sublcasses of the `Comm`
class.  The `Comm.Is_inter` method (and `Comm.Is_intra`, provided for
convenience but not part of the MPI specification) is defined for
communicator objects and can be used to determine the particular
communicator class.

The two predefined intracommunicator instances are available:
`COMM_SELF` and `COMM_WORLD`. From them, new communicators can be
created as needed.

The number of processes in a communicator and the calling process rank
can be respectively obtained with methods `Comm.Get_size` and
`Comm.Get_rank`. The associated process group can be retrieved from a
communicator by calling the `Comm.Get_group` method, which returns an
instance of the `Group` class. Set operations with `Group` objects
like like `Group.Union`, `Group.Intersection` and `Group.Difference`
are fully supported, as well as the creation of new communicators from
these groups using `Comm.Create` and `Intracomm.Create_group`.

New communicator instances can be obtained with the `Comm.Clone`,
`Comm.Dup` and `Comm.Split` methods, as well methods
`Intracomm.Create_intercomm` and `Intercomm.Merge`.

Virtual topologies (`Cartcomm`, `Graphcomm` and `Distgraphcomm`
classes, which are specializations of the `Intracomm` class) are fully
supported. New instances can be obtained from intracommunicator
instances with factory methods `Intracomm.Create_cart` and
`Intracomm.Create_graph`.


Point-to-Point Communications
-----------------------------

Point to point communication is a fundamental capability of message
passing systems. This mechanism enables the transmission of data
between a pair of processes, one side sending, the other receiving.

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

In *MPI for Python*, the `Comm.Send`, `Comm.Recv` and `Comm.Sendrecv`
methods of communicator objects provide support for blocking
point-to-point communications within `Intracomm` and `Intercomm`
instances. These methods can communicate memory buffers. The variants
`Comm.send`, `Comm.recv` and `Comm.sendrecv` can communicate general
Python objects.

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

In *MPI for Python*, the `Comm.Isend` and `Comm.Irecv` methods
initiate send and receive operations, respectively. These methods
return a `Request` instance, uniquely identifying the started
operation.  Its completion can be managed using the `Request.Test`,
`Request.Wait` and `Request.Cancel` methods. The management of
`Request` objects and associated memory buffers involved in
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

In *MPI for Python*, the `Comm.Send_init` and `Comm.Recv_init` methods
create persistent requests for a send and receive operation,
respectively.  These methods return an instance of the `Prequest`
class, a subclass of the `Request` class. The actual communication can
be effectively started using the `Prequest.Start` method, and its
completion can be managed as previously described.


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

In *MPI for Python*, the `Comm.Bcast`, `Comm.Scatter`, `Comm.Gather`,
`Comm.Allgather`, `Comm.Alltoall` methods provide support for
collective communications of memory buffers. The lower-case variants
`Comm.bcast`, `Comm.scatter`, `Comm.gather`, `Comm.allgather` and
`Comm.alltoall` can communicate general Python objects.  The vector
variants (which can communicate different amounts of data to each
process) `Comm.Scatterv`, `Comm.Gatherv`, `Comm.Allgatherv`,
`Comm.Alltoallv` and `Comm.Alltoallw` are also supported, they can
only communicate objects exposing memory buffers.

Global reducion operations on memory buffers are accessible through
the `Comm.Reduce`, `Comm.Reduce_scatter`, `Comm.Allreduce`,
`Intracomm.Scan` and `Intracomm.Exscan` methods. The lower-case
variants `Comm.reduce`, `Comm.allreduce`, `Intracomm.scan` and
`Intracomm.exscan` can communicate general Python objects; however,
the actual required reduction computations are performed sequentially
at some process. All the predefined (i.e., `SUM`, `PROD`, `MAX`, etc.)
reduction operations can be applied.


Support for GPU-aware MPI
-------------------------

Several MPI implementations, including Open MPI and MVAPICH, support
passing GPU pointers to MPI calls to avoid explicit data movement
between host and device. On the Python side, support for handling GPU
arrays have been implemented in many libraries related GPU computation
such as `CuPy`_, `Numba`_, `PyTorch`_, and `PyArrow`_. To maximize
interoperability across library boundaries, two kinds of zero-copy
data exchange protocols have been defined and agreed upon: `DLPack
<dlpack:python-spec>` and `CUDA Array Interface (CAI)
<numba:cuda-array-interface>`.

.. _CuPy: https://cupy.dev/
.. _Numba: https://numba.pydata.org/
.. _PyTorch: https://pytorch.org/
.. _PyArrow: https://arrow.apache.org/docs/python/

*MPI for Python* provides an experimental support for GPU-aware MPI.
This feature requires:

1. mpi4py is built against a GPU-aware MPI library.

2. The Python GPU arrays are compliant with either of the protocols.

See the :doc:`tutorial` section for further information. We note that

* Whether or not a MPI call can work for GPU arrays depends on the
  underlying MPI implementation, not on mpi4py.

* This support is currently experimental and subject to change in the
  future.


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

In *MPI for Python*, new independent process groups can be created by
calling the `Intracomm.Spawn` method within an intracommunicator.
This call returns a new intercommunicator (i.e., an `Intercomm`
instance) at the parent process group. The child process group can
retrieve the matching intercommunicator by calling the
`Comm.Get_parent` class method. At each side, the new
intercommunicator can be used to perform point to point and collective
communications between the parent and child groups of processes.

Alternatively, disjoint groups of processes can establish
communication using a client/server approach. Any server application
must first call the `Open_port` function to open a *port* and the
`Publish_name` function to publish a provided *service*, and next call
the `Intracomm.Accept` method.  Any client applications can first find
a published *service* by calling the `Lookup_name` function, which
returns the *port* where a server can be contacted; and next call the
`Intracomm.Connect` method. Both `Intracomm.Accept` and
`Intracomm.Connect` methods return an `Intercomm` instance. When
connection between client/server processes is no longer needed, all of
them must cooperatively call the `Comm.Disconnect`
method. Additionally, server applications should release resources by
calling the `Unpublish_name` and `Close_port` functions.


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
instances of the `Win` class. New window objects are created by
calling the `Win.Create` method at all processes within a communicator
and specifying a memory buffer . When a window instance is no longer
needed, the `Win.Free` method should be called.

The three one-sided MPI operations for remote write, read and
reduction are available through calling the methods `Win.Put`,
`Win.Get`, and `Win.Accumulate` respectively within a `Win` instance.
These methods need an integer rank identifying the target process and
an integer offset relative the base address of the remote memory block
being accessed.

The one-sided operations read, write, and reduction are implicitly
nonblocking, and must be synchronized by using two primary modes.
Active target synchronization requires the origin process to call the
`Win.Start` and `Win.Complete` methods at the origin process, and
target process cooperates by calling the `Win.Post` and `Win.Wait`
methods. There is also a collective variant provided by the
`Win.Fence` method. Passive target synchronization is more lenient,
only the origin process calls the `Win.Lock` and `Win.Unlock`
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

In *MPI for Python*, all MPI input/output operations are performed
through instances of the `File` class. File handles are obtained by
calling the `File.Open` method at all processes within a communicator
and providing a file name and the intended access mode.  After use,
they must be closed by calling the `File.Close` method.  Files even
can be deleted by calling method `File.Delete`.

After creation, files are typically associated with a per-process
*view*. The view defines the current set of data visible and
accessible from an open file as an ordered set of elementary
datatypes. This data layout can be set and queried with the
`File.Set_view` and `File.Get_view` methods respectively.

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

Module functions `Init` or `Init_thread` and `Finalize` provide MPI
initialization and finalization respectively. Module functions
`Is_initialized` and `Is_finalized` provide the respective tests for
initialization and finalization.

.. note::

   :c:func:`MPI_Init` or :c:func:`MPI_Init_thread` is actually called
   when you import the :mod:`~mpi4py.MPI` module from the
   :mod:`mpi4py` package, but only if MPI is not already
   initialized. In such case, calling `Init` or `Init_thread` from
   Python is expected to generate an MPI error, and in turn an
   exception will be raised.

.. note::

   :c:func:`MPI_Finalize` is registered (by using Python C/API
   function :c:func:`Py_AtExit`) for being automatically called when
   Python processes exit, but only if :mod:`mpi4py` actually
   initialized MPI. Therefore, there is no need to call `Finalize`
   from Python to ensure MPI finalization.

Implementation Information
^^^^^^^^^^^^^^^^^^^^^^^^^^

* The MPI version number can be retrieved from module function
  `Get_version`. It returns a two-integer tuple ``(version,
  subversion)``.

* The `Get_processor_name` function can be used to access the
  processor name.

* The values of predefined attributes attached to the world
  communicator can be obtained by calling the `Comm.Get_attr` method
  within the `COMM_WORLD` instance.

Timers
^^^^^^

MPI timer functionalities are available through the `Wtime` and
`Wtick` functions.

Error Handling
^^^^^^^^^^^^^^

In order to facilitate handle sharing with other Python modules
interfacing MPI-based parallel libraries, the predefined MPI error
handlers `ERRORS_RETURN` and `ERRORS_ARE_FATAL` can be assigned to and
retrieved from communicators using methods `Comm.Set_errhandler` and
`Comm.Get_errhandler`, and similarly for windows and files. New custom
error handlers can be created with `Comm.Create_errhandler`.

When the predefined error handler `ERRORS_RETURN` is set, errors
returned from MPI calls within Python code will raise an instance of
the exception class `Exception`, which is a subclass of the standard
Python exception `python:RuntimeError`.

.. note::

   After import, mpi4py overrides the default MPI rules governing
   inheritance of error handlers. The `ERRORS_RETURN` error handler is
   set in the predefined `COMM_SELF` and `COMM_WORLD` communicators,
   as well as any new `Comm`, `Win`, or `File` instance created
   through mpi4py. If you ever pass such handles to C/C++/Fortran
   library code, it is recommended to set the `ERRORS_ARE_FATAL` error
   handler on them to ensure MPI errors do not pass silently.

.. warning::

   Importing with ``from mpi4py.MPI import *`` will cause a name
   clashing with the standard Python `python:Exception` base class.
