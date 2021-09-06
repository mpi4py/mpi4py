mpi4py.futures
==============

.. module:: mpi4py.futures
   :synopsis: Execute computations concurrently using MPI processes.

.. versionadded:: 3.0.0

This package provides a high-level interface for asynchronously executing
callables on a pool of worker processes using MPI for inter-process
communication.

The :mod:`mpi4py.futures` package is based on :mod:`concurrent.futures` from
the Python standard library. More precisely, :mod:`mpi4py.futures` provides the
:class:`MPIPoolExecutor` class as a concrete implementation of the abstract
class :class:`~concurrent.futures.Executor`.  The
:meth:`~concurrent.futures.Executor.submit` interface schedules a callable to
be executed asynchronously and returns a :class:`~concurrent.futures.Future`
object representing the execution of the callable.
:class:`~concurrent.futures.Future` instances can be queried for the call
result or exception. Sets of :class:`~concurrent.futures.Future` instances can
be passed to the :func:`~concurrent.futures.wait` and
:func:`~concurrent.futures.as_completed` functions.

.. seealso::

   Module :mod:`concurrent.futures`
      Documentation of the :mod:`concurrent.futures` standard module.


MPIPoolExecutor
---------------

The :class:`MPIPoolExecutor` class uses a pool of MPI processes to execute
calls asynchronously. By performing computations in separate processes, it
allows to side-step the :term:`global interpreter lock` but also means that
only picklable objects can be executed and returned. The :mod:`__main__` module
must be importable by worker processes, thus :class:`MPIPoolExecutor` instances
may not work in the interactive interpreter.

:class:`MPIPoolExecutor` takes advantage of the dynamic process management
features introduced in the MPI-2 standard. In particular, the
`MPI.Intracomm.Spawn` method of `MPI.COMM_SELF` is used in the master (or
parent) process to spawn new worker (or child) processes running a Python
interpreter. The master process uses a separate thread (one for each
:class:`MPIPoolExecutor` instance) to communicate back and forth with the
workers.  The worker processes serve the execution of tasks in the main (and
only) thread until they are signaled for completion.

.. note::

   The worker processes must import the main script in order to *unpickle* any
   callable defined in the :mod:`__main__` module and submitted from the master
   process. Furthermore, the callables may need access to other global
   variables. At the worker processes, :mod:`mpi4py.futures` executes the main
   script code (using the :mod:`runpy` module) under the :mod:`__worker__`
   namespace to define the :mod:`__main__` module. The :mod:`__main__` and
   :mod:`__worker__` modules are added to :data:`sys.modules` (both at the
   master and worker processes) to ensure proper *pickling* and *unpickling*.

.. warning::

   During the initial import phase at the workers, the main script cannot
   create and use new :class:`MPIPoolExecutor` instances. Otherwise, each
   worker would attempt to spawn a new pool of workers, leading to infinite
   recursion. :mod:`mpi4py.futures` detects such recursive attempts to spawn
   new workers and aborts the MPI execution environment. As the main script
   code is run under the :mod:`__worker__` namespace, the easiest way to avoid
   spawn recursion is using the idiom :code:`if __name__ == '__main__': ...` in
   the main script.

.. class:: MPIPoolExecutor(max_workers=None, \
                           initializer=None, initargs=(), **kwargs)

   An :class:`~concurrent.futures.Executor` subclass that executes calls
   asynchronously using a pool of at most *max_workers* processes.  If
   *max_workers* is `None` or not given, its value is determined from the
   :envvar:`MPI4PY_FUTURES_MAX_WORKERS` environment variable if set, or the MPI
   universe size if set, otherwise a single worker process is spawned.  If
   *max_workers* is lower than or equal to ``0``, then a :exc:`ValueError` will
   be raised.

   *initializer* is an optional callable that is called at the start of each
   worker process before executing any tasks; *initargs* is a tuple of
   arguments passed to the initializer. If *initializer* raises an exception,
   all pending tasks and any attempt to submit new tasks to the pool will raise
   a :exc:`~concurrent.futures.BrokenExecutor` exception.

   Other parameters:

   * *python_exe*: Path to the Python interpreter executable used to spawn
     worker processes, otherwise :data:`sys.executable` is used.

   * *python_args*: :class:`list` or iterable with additional command line
     flags to pass to the Python executable. Command line flags determined from
     inspection of :data:`sys.flags`, :data:`sys.warnoptions` and
     :data:`sys._xoptions` in are passed unconditionally.

   * *mpi_info*: :class:`dict` or iterable yielding ``(key, value)`` pairs.
     These ``(key, value)`` pairs are passed (through an `MPI.Info` object) to
     the `MPI.Intracomm.Spawn` call used to spawn worker processes. This
     mechanism allows telling the MPI runtime system where and how to start the
     processes. Check the documentation of the backend MPI implementation about
     the set of keys it interprets and the corresponding format for values.

   * *globals*: :class:`dict` or iterable yielding ``(name, value)`` pairs to
     initialize the main module namespace in worker processes.

   * *main*: If set to `False`, do not import the :mod:`__main__` module in
     worker processes. Setting *main* to `False` prevents worker processes
     from accessing definitions in the parent :mod:`__main__` namespace.

   * *path*: :class:`list` or iterable with paths to append to :data:`sys.path`
     in worker processes to extend the :ref:`module search path
     <python:tut-searchpath>`.

   * *wdir*: Path to set the current working directory in worker processes
     using :func:`os.chdir()`. The initial working directory is set by the MPI
     implementation. Quality MPI implementations should honor a ``wdir`` info
     key passed through *mpi_info*, although such feature is not mandatory.

   * *env*: :class:`dict` or iterable yielding ``(name, value)`` pairs with
     environment variables to update :data:`os.environ` in worker processes.
     The initial environment is set by the MPI implementation. MPI
     implementations may allow setting the initial environment through
     *mpi_info*, however such feature is not required nor recommended by the
     MPI standard.

   * *use_pkl5*: If set to `True`, use :mod:`pickle5` with out-of-band buffers
     for interprocess communication. If *use_pkl5* is set to `None` or not
     given, its value is determined from the :envvar:`MPI4PY_FUTURES_USE_PKL5`
     environment variable. Using :mod:`pickle5` with out-of-band buffers may
     benefit applications dealing with large buffer-like objects like NumPy
     arrays. See :mod:`mpi4py.util.pkl5` for additional information.

   .. method:: submit(func, *args, **kwargs)

      Schedule the callable, *func*, to be executed as ``func(*args,
      **kwargs)`` and returns a :class:`~concurrent.futures.Future` object
      representing the execution of the callable. ::

         executor = MPIPoolExecutor(max_workers=1)
         future = executor.submit(pow, 321, 1234)
         print(future.result())

   .. method:: map(func, *iterables, timeout=None, chunksize=1, **kwargs)

      Equivalent to :func:`map(func, *iterables) <python:map>` except *func* is
      executed asynchronously and several calls to *func* may be made
      concurrently, out-of-order, in separate processes.  The returned iterator
      raises a :exc:`~concurrent.futures.TimeoutError` if
      :meth:`~iterator.__next__` is called and the result isn't available after
      *timeout* seconds from the original call to :meth:`~MPIPoolExecutor.map`.
      *timeout* can be an int or a float.  If *timeout* is not specified or
      `None`, there is no limit to the wait time.  If a call raises an
      exception, then that exception will be raised when its value is retrieved
      from the iterator. This method chops *iterables* into a number of chunks
      which it submits to the pool as separate tasks. The (approximate) size of
      these chunks can be specified by setting *chunksize* to a positive
      integer. For very long iterables, using a large value for *chunksize* can
      significantly improve performance compared to the default size of one. By
      default, the returned iterator yields results in-order, waiting for
      successive tasks to complete . This behavior can be changed by passing
      the keyword argument *unordered* as `True`, then the result iterator
      will yield a result as soon as any of the tasks complete. ::

         executor = MPIPoolExecutor(max_workers=3)
         for result in executor.map(pow, [2]*32, range(32)):
             print(result)

   .. method:: starmap(func, iterable, timeout=None, chunksize=1, **kwargs)

      Equivalent to :func:`itertools.starmap(func, iterable)
      <itertools.starmap>`. Used instead of :meth:`~MPIPoolExecutor.map` when
      argument parameters are already grouped in tuples from a single iterable
      (the data has been "pre-zipped"). :func:`map(func, *iterable) <map>` is
      equivalent to :func:`starmap(func, zip(*iterable)) <starmap>`. ::

         executor = MPIPoolExecutor(max_workers=3)
         iterable = ((2, n) for n in range(32))
         for result in executor.starmap(pow, iterable):
             print(result)

   .. method:: shutdown(wait=True, cancel_futures=False)

      Signal the executor that it should free any resources that it is using
      when the currently pending futures are done executing.  Calls to
      :meth:`~MPIPoolExecutor.submit` and :meth:`~MPIPoolExecutor.map` made
      after :meth:`~MPIPoolExecutor.shutdown` will raise :exc:`RuntimeError`.

      If *wait* is `True` then this method will not return until all the
      pending futures are done executing and the resources associated with the
      executor have been freed.  If *wait* is `False` then this method will
      return immediately and the resources associated with the executor will be
      freed when all pending futures are done executing.  Regardless of the
      value of *wait*, the entire Python program will not exit until all
      pending futures are done executing.

      If *cancel_futures* is `True`, this method will cancel all pending
      futures that the executor has not started running. Any futures that
      are completed or running won't be cancelled, regardless of the value
      of *cancel_futures*.

      You can avoid having to call this method explicitly if you use the
      :keyword:`with` statement, which will shutdown the executor instance
      (waiting as if :meth:`~MPIPoolExecutor.shutdown` were called with *wait*
      set to `True`). ::

         import time
         with MPIPoolExecutor(max_workers=1) as executor:
             future = executor.submit(time.sleep, 2)
         assert future.done()

   .. method:: bootup(wait=True)

      Signal the executor that it should allocate eagerly any required
      resources (in particular, MPI worker processes). If *wait* is `True`,
      then :meth:`~MPIPoolExecutor.bootup` will not return until the executor
      resources are ready to process submissions.  Resources are automatically
      allocated in the first call to :meth:`~MPIPoolExecutor.submit`, thus
      calling :meth:`~MPIPoolExecutor.bootup` explicitly is seldom needed.


.. envvar:: MPI4PY_FUTURES_MAX_WORKERS

   If the *max_workers* parameter to :class:`MPIPoolExecutor` is `None` or not
   given, the :envvar:`MPI4PY_FUTURES_MAX_WORKERS` environment variable
   provides a fallback value for the maximum number of MPI worker processes to
   spawn.

.. envvar:: MPI4PY_FUTURES_USE_PKL5

   If the *use_pkl5* keyword argument to :class:`MPIPoolExecutor` is `None` or
   not given, the :envvar:`MPI4PY_FUTURES_USE_PKL5` environment variable
   provides a fallback value for whether the executor should use :mod:`pickle5`
   with out-of-band buffers for interprocess communication. Accepted values are
   ``0`` and ``1`` (interpreted as `False` and `True`, respectively), and
   strings specifying a `YAML boolean`_ value (case-insensitive). Using
   :mod:`pickle5` with out-of-band buffers may benefit applications dealing
   with large buffer-like objects like NumPy arrays. See
   :mod:`mpi4py.util.pkl5` for additional information.

   .. _YAML boolean: https://yaml.org/type/bool.html

.. note::

   As the master process uses a separate thread to perform MPI communication
   with the workers, the backend MPI implementation should provide support for
   `MPI.THREAD_MULTIPLE`. However, some popular MPI implementations do not
   support yet concurrent MPI calls from multiple threads. Additionally, users
   may decide to initialize MPI with a lower level of thread support. If the
   level of thread support in the backend MPI is less than
   `MPI.THREAD_MULTIPLE`, :mod:`mpi4py.futures` will use a global lock to
   serialize MPI calls. If the level of thread support is less than
   `MPI.THREAD_SERIALIZED`, :mod:`mpi4py.futures` will emit a
   :exc:`RuntimeWarning`.

.. warning::

   If the level of thread support in the backend MPI is less than
   `MPI.THREAD_SERIALIZED` (i.e, it is either `MPI.THREAD_SINGLE` or
   `MPI.THREAD_FUNNELED`), in theory :mod:`mpi4py.futures` cannot be
   used. Rather than raising an exception, :mod:`mpi4py.futures` emits a
   warning and takes a "cross-fingers" attitude to continue execution in the
   hope that serializing MPI calls with a global lock will actually work.


MPICommExecutor
---------------

Legacy MPI-1 implementations (as well as some vendor MPI-2 implementations) do
not support the dynamic process management features introduced in the MPI-2
standard. Additionally, job schedulers and batch systems in supercomputing
facilities may pose additional complications to applications using the
:c:func:`MPI_Comm_spawn` routine.

With these issues in mind, :mod:`mpi4py.futures` supports an additonal, more
traditional, SPMD-like usage pattern requiring MPI-1 calls only. Python
applications are started the usual way, e.g., using the :program:`mpiexec`
command. Python code should make a collective call to the
:class:`MPICommExecutor` context manager to partition the set of MPI processes
within a MPI communicator in one master processes and many workers
processes. The master process gets access to an :class:`MPIPoolExecutor`
instance to submit tasks. Meanwhile, the worker process follow a different
execution path and team-up to execute the tasks submitted from the master.

Besides alleviating the lack of dynamic process managment features in legacy
MPI-1 or partial MPI-2 implementations, the :class:`MPICommExecutor` context
manager may be useful in classic MPI-based Python applications willing to take
advantage of the simple, task-based, master/worker approach available in the
:mod:`mpi4py.futures` package.

.. class:: MPICommExecutor(comm=None, root=0)

   Context manager for :class:`MPIPoolExecutor`. This context manager splits a
   MPI (intra)communicator *comm* (defaults to `MPI.COMM_WORLD` if not provided
   or `None`) in two disjoint sets: a single master process (with rank *root*
   in *comm*) and the remaining worker processes. These sets are then connected
   through an intercommunicator.  The target of the :keyword:`with` statement
   is assigned either an :class:`MPIPoolExecutor` instance (at the master) or
   `None` (at the workers). ::

      from mpi4py import MPI
      from mpi4py.futures import MPICommExecutor

      with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
          if executor is not None:
             future = executor.submit(abs, -42)
             assert future.result() == 42
             answer = set(executor.map(abs, [-42, 42]))
             assert answer == {42}

.. warning::

   If :class:`MPICommExecutor` is passed a communicator of size one (e.g.,
   `MPI.COMM_SELF`), then the executor instace assigned to the target of the
   :keyword:`with` statement will execute all submitted tasks in a single
   worker thread, thus ensuring that task execution still progress
   asynchronously. However, the :term:`GIL` will prevent the main and worker
   threads from running concurrently in multicore processors. Moreover, the
   thread context switching may harm noticeably the performance of CPU-bound
   tasks. In case of I/O-bound tasks, the :term:`GIL` is not usually an issue,
   however, as a single worker thread is used, it progress one task at a
   time. We advice against using :class:`MPICommExecutor` with communicators of
   size one and suggest refactoring your code to use instead a
   :class:`~concurrent.futures.ThreadPoolExecutor`.


Command line
------------

Recalling the issues related to the lack of support for dynamic process
managment features in MPI implementations, :mod:`mpi4py.futures` supports an
alternative usage pattern where Python code (either from scripts, modules, or
zip files) is run under command line control of the :mod:`mpi4py.futures`
package by passing :samp:`-m mpi4py.futures` to the :program:`python`
executable.  The ``mpi4py.futures`` invocation should be passed a *pyfile* path
to a script (or a zipfile/directory containing a :file:`__main__.py` file).
Additionally, ``mpi4py.futures`` accepts :samp:`-m {mod}` to execute a module
named *mod*, :samp:`-c {cmd}` to execute a command string *cmd*, or even
:samp:`-` to read commands from standard input (:data:`sys.stdin`).
Summarizing, :samp:`mpi4py.futures` can be invoked in the following ways:

* :samp:`$ mpiexec -n {numprocs} python -m mpi4py.futures {pyfile} [arg] ...`
* :samp:`$ mpiexec -n {numprocs} python -m mpi4py.futures -m {mod} [arg] ...`
* :samp:`$ mpiexec -n {numprocs} python -m mpi4py.futures -c {cmd} [arg] ...`
* :samp:`$ mpiexec -n {numprocs} python -m mpi4py.futures - [arg] ...`

Before starting the main script execution, :mod:`mpi4py.futures` splits
`MPI.COMM_WORLD` in one master (the process with rank 0 in `MPI.COMM_WORLD`) and
*numprocs - 1* workers and connects them through an MPI intercommunicator.
Afterwards, the master process proceeds with the execution of the user script
code, which eventually creates :class:`MPIPoolExecutor` instances to submit
tasks. Meanwhile, the worker processes follow a different execution path to
serve the master.  Upon successful termination of the main script at the master,
the entire MPI execution environment exists gracefully. In case of any unhandled
exception in the main script, the master process calls
``MPI.COMM_WORLD.Abort(1)`` to prevent deadlocks and force termination of entire
MPI execution environment.

.. warning::

   Running scripts under command line control of :mod:`mpi4py.futures` is quite
   similar to executing a single-process application that spawn additional
   workers as required. However, there is a very important difference users
   should be aware of. All :class:`~MPIPoolExecutor` instances created at the
   master will share the pool of workers. Tasks submitted at the master from
   many different executors will be scheduled for execution in random order as
   soon as a worker is idle. Any executor can easily starve all the workers
   (e.g., by calling :func:`MPIPoolExecutor.map` with long iterables). If that
   ever happens, submissions from other executors will not be serviced until
   free workers are available.

.. seealso::

   :ref:`python:using-on-cmdline`
      Documentation on Python command line interface.

Examples
--------

The following :file:`julia.py` script computes the `Julia set`_ and dumps an
image to disk in binary `PGM`_ format. The code starts by importing
:class:`MPIPoolExecutor` from the :mod:`mpi4py.futures` package. Next, some
global constants and functions implement the computation of the Julia set. The
computations are protected with the standard :code:`if __name__ == '__main__':
...` idiom.  The image is computed by whole scanlines submitting all these
tasks at once using the :class:`~MPIPoolExecutor.map` method. The result
iterator yields scanlines in-order as the tasks complete. Finally, each
scanline is dumped to disk.

.. _`Julia set`: https://en.wikipedia.org/wiki/Julia_set
.. _`PGM`: http://netpbm.sourceforge.net/doc/pgm.html

.. code-block:: python
   :name: julia-py
   :caption: :file:`julia.py`
   :emphasize-lines: 1,26,28,29
   :linenos:

   from mpi4py.futures import MPIPoolExecutor

   x0, x1, w = -2.0, +2.0, 640*2
   y0, y1, h = -1.5, +1.5, 480*2
   dx = (x1 - x0) / w
   dy = (y1 - y0) / h

   c = complex(0, 0.65)

   def julia(x, y):
       z = complex(x, y)
       n = 255
       while abs(z) < 3 and n > 1:
           z = z**2 + c
           n -= 1
       return n

   def julia_line(k):
       line = bytearray(w)
       y = y1 - k * dy
       for j in range(w):
           x = x0 + j * dx
           line[j] = julia(x, y)
       return line

   if __name__ == '__main__':

       with MPIPoolExecutor() as executor:
           image = executor.map(julia_line, range(h))
           with open('julia.pgm', 'wb') as f:
               f.write(b'P5 %d %d %d\n' % (w, h, 255))
               for line in image:
                   f.write(line)

The recommended way to execute the script is by using the :program:`mpiexec`
command specifying one MPI process (master) and (optional but recommended) the
desired MPI universe size, which determines the number of additional
dynamically spawned processes (workers). The MPI universe size is provided
either by a batch system or set by the user via command-line arguments to
:program:`mpiexec` or environment variables. Below we provide examples for
MPICH and Open MPI implementations [#]_. In all of these examples, the
:program:`mpiexec` command launches a single master process running the Python
interpreter and executing the main script. When required, :mod:`mpi4py.futures`
spawns the pool of 16 worker processes. The master submits tasks to the workers
and waits for the results. The workers receive incoming tasks, execute them,
and send back the results to the master.

When using MPICH implementation or its derivatives based on the Hydra process
manager, users can set the MPI universe size via the ``-usize`` argument to
:program:`mpiexec`::

  $ mpiexec -n 1 -usize 17 python julia.py

or, alternatively, by setting the :envvar:`MPIEXEC_UNIVERSE_SIZE` environment
variable::

  $ MPIEXEC_UNIVERSE_SIZE=17 mpiexec -n 1 python julia.py

In the Open MPI implementation, the MPI universe size can be set via the
``-host`` argument to :program:`mpiexec`::

  $ mpiexec -n 1 -host <hostname>:17 python julia.py

Another way to specify the number of workers is to use the
:mod:`mpi4py.futures`-specific environment variable
:envvar:`MPI4PY_FUTURES_MAX_WORKERS`::

  $ MPI4PY_FUTURES_MAX_WORKERS=16 mpiexec -n 1 python julia.py

Note that in this case, the MPI universe size is ignored.

Alternatively, users may decide to execute the script in a more traditional
way, that is, all the MPI processes are started at once. The user script is run
under command-line control of :mod:`mpi4py.futures` passing the :ref:`-m
<python:using-on-cmdline>` flag to the :program:`python` executable::

  $ mpiexec -n 17 python -m mpi4py.futures julia.py

As explained previously, the 17 processes are partitioned in one master and 16
workers. The master process executes the main script while the workers execute
the tasks submitted by the master.

.. [#] When using an MPI implementation other than MPICH or Open MPI, please
   check the documentation of the implementation and/or batch
   system for the ways to specify the desired MPI universe size.


.. glossary::

   GIL
     See :term:`global interpreter lock`.


.. Local variables:
.. fill-column: 79
.. End:
