mpi4py.run
==========

.. module:: mpi4py.run
   :synopsis: Run Python code using ``-m mpi4py``.

.. versionadded:: 2.1.0

At import time, :mod:`mpi4py` initializes the MPI execution environment calling
:c:func:`MPI_Init_thread` and installs an exit hook to automatically call
:c:func:`MPI_Finalize` just before the Python process terminates. Additionally,
:mod:`mpi4py` overrides the default :const:`MPI.ERRORS_ARE_FATAL` error handler
in favor of :const:`MPI.ERRORS_RETURN`, which allows translating MPI errors in
Python exceptions. These departures from standard MPI behavior may be
controversial, but are quite convenient within the highly dynamic Python
programming environment. Third-party code using :mod:`mpi4py` can just ``from
mpi4py import MPI`` and perform MPI calls without the tedious
initialization/finalization handling.  MPI errors, once translated
automatically to Python exceptions, can be dealt with the common
:keyword:`try`...\ :keyword:`except`...\ :keyword:`finally` clauses; unhandled
MPI exceptions will print a traceback which helps in locating problems in
source code.

Unfortunately, the interplay of automatic MPI finalization and unhandled
exceptions may lead to deadlocks. In unattended runs, these deadlocks will
drain the battery of your laptop, or burn precious allocation hours in your
supercomputing facility.

Consider the following snippet of Python code. Assume this code is stored in a
standard Python script file and run with :command:`mpiexec` in two or more
processes. ::

   from mpi4py import MPI
   assert MPI.COMM_WORLD.Get_size() > 1
   rank = MPI.COMM_WORLD.Get_rank()
   if rank == 0:
       1/0
       MPI.COMM_WORLD.send(None, dest=1, tag=42)
   elif rank == 1:
       MPI.COMM_WORLD.recv(source=0, tag=42)

Process 0 raises :exc:`ZeroDivisionError` exception before performing a send
call to process 1. As the exception is not handled, the Python interpreter
running in process 0 will proceed to exit with non-zero status. However, as
:mod:`mpi4py` installed a finalizer hook to call :c:func:`MPI_Finalize` before
exit, process 0 will block waiting for other processes to also enter the
:c:func:`MPI_Finalize` call. Meanwhile, process 1 will block waiting for a
message to arrive from process 0, thus never reaching to
:c:func:`MPI_Finalize`. The whole MPI execution environment is irremediably in
a deadlock state.

To alleviate this issue, :mod:`mpi4py` offers a simple, alternative command
line execution mechanism based on using the :ref:`-m <python:using-on-cmdline>`
flag and implemented with the :mod:`runpy` module. To use this features, Python
code should be run passing ``-m mpi4py`` in the command line invoking the
Python interpreter. In case of unhandled exceptions, the finalizer hook will
call :c:func:`MPI_Abort` on the :c:data:`MPI_COMM_WORLD` communicator, thus
effectively aborting the MPI execution environment.

.. warning::

   When a process is forced to abort, resources (e.g. open files) are not
   cleaned-up and any registered finalizers (either with the :mod:`atexit`
   module, the Python C/API function :c:func:`Py_AtExit()`, or even the C
   standard library function :c:func:`atexit`) will not be executed. Thus,
   aborting execution is an extremely impolite way of ensuring process
   termination. However, MPI provides no other mechanism to recover from a
   deadlock state.

Interface options
-----------------

The use of ``-m mpi4py`` to execute Python code on the command line resembles
that of the Python interpreter.

* :samp:`mpiexec -n {numprocs} python -m mpi4py {pyfile} [arg] ...`
* :samp:`mpiexec -n {numprocs} python -m mpi4py -m {mod} [arg] ...`
* :samp:`mpiexec -n {numprocs} python -m mpi4py -c {cmd} [arg] ...`
* :samp:`mpiexec -n {numprocs} python -m mpi4py - [arg] ...`

.. describe:: <pyfile>

   Execute the Python code contained in *pyfile*, which must be a filesystem
   path referring to either a Python file, a directory containing a
   :file:`__main__.py` file, or a zipfile containing a :file:`__main__.py`
   file.

.. cmdoption:: -m <mod>

   Search :data:`sys.path` for the named module *mod* and execute its contents.

.. cmdoption:: -c <cmd>

   Execute the Python code in the *cmd* string command.

.. describe:: -

   Read commands from standard input (:data:`sys.stdin`).

.. seealso::

   :ref:`python:using-on-cmdline`
        Documentation on Python command line interface.


.. Local variables:
.. fill-column: 79
.. End:
