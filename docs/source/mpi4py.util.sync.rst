mpi4py.util.sync
----------------

.. module:: mpi4py.util.sync
   :synopsis: Synchronization utilities.

.. versionadded:: 4.0.0

The :mod:`mpi4py.util.sync` module provides parallel synchronization
utilities.

Sequential execution
++++++++++++++++++++

.. autoclass:: mpi4py.util.sync.Sequential

   Context manager for sequential execution within a group of MPI processes.

   The implementation is based in MPI-1 point-to-point communication. A process
   with rank *i* waits in a blocking receive until the previous process rank
   *i-1* finish executing and signals the next rank *i* with a send.

   .. automethod:: __init__
   .. automethod:: __enter__
   .. automethod:: __exit__
   .. automethod:: begin
   .. automethod:: end

Global counter
++++++++++++++

.. autoclass:: mpi4py.util.sync.Counter

   Produce consecutive values within a group of MPI processes. The counter
   interface is close to that of `itertools.count`.

   The implementation is based in MPI-3 one-sided operations. A root process
   (typically rank ``0``) holds the counter, and its value is queried and
   incremented with an atomic RMA *fetch-and-add* operation.

   .. automethod:: __init__
   .. automethod:: __iter__
   .. automethod:: __next__
   .. automethod:: next
   .. automethod:: free

Mutual exclusion
++++++++++++++++

.. autoclass:: mpi4py.util.sync.Mutex

   Establish a critical section or mutual exclusion among MPI processes. The
   mutex interface is close to that of `threading.Lock`. However, its intended
   uses and specific semantics are somewhat different:

   * A mutex should be used within a group of MPI processes, not threads.
   * Once acquired, a mutex is held and owned by a process until released.
   * Trying to acquire a mutex already held raises `RuntimeError`.
   * Trying to release a mutex not yet held raises `RuntimeError`.

   This mutex implementation uses the scalable and fair spinlock algorithm from
   [mcs-paper]_ and took inspiration from the MPI-3 RMA implementation of
   [uam-book]_.

   .. [mcs-paper] John M. Mellor-Crummey and Michael L. Scott.
      Algorithms for scalable synchronization on shared-memory multiprocessors.
      ACM Transactions on Computer Systems, 9(1):21-65, February 1991.
      https://doi.org/10.1145/103727.103729

   .. [uam-book] William Gropp, Torsten Hoefler, Rajeev Thakur, Ewing Lusk.
      Using Advanced MPI - Modern Features of the Message-Passing Interface.
      Chapter 4, Section 4.7, Pages 130-131. The MIT Press, November 2014.
      https://mitpress.mit.edu/9780262527637/using-advanced-mpi/

   .. automethod:: __init__
   .. automethod:: __enter__
   .. automethod:: __exit__
   .. automethod:: acquire
   .. automethod:: release
   .. automethod:: locked
   .. automethod:: free

.. autoclass:: mpi4py.util.sync.RMutex

   Establish a critical section or mutual exclusion among MPI processes. The
   mutex interface is close to that of `threading.RLock`, allowing for
   recursive acquire and release operations. However, the mutex should be used
   within a group of MPI processes, not threads.

   The implementation is based on a `Mutex` providing mutual exclusion and a
   counter tracking the recursion level.

   .. automethod:: __init__
   .. automethod:: __enter__
   .. automethod:: __exit__
   .. automethod:: acquire
   .. automethod:: release
   .. automethod:: locked
   .. automethod:: count
   .. automethod:: free


Examples
++++++++

.. code-block:: python
   :name: test-sync-1
   :caption: :file:`test-sync-1.py`
   :emphasize-lines:  2,6-9
   :linenos:

   from mpi4py import MPI
   from mpi4py.util.sync import Counter, Sequential

   comm = MPI.COMM_WORLD

   counter = Counter(comm)
   with Sequential(comm):
      value = next(counter)
   counter.free()

   assert comm.rank == value

.. code-block:: python
   :name: test-sync-2
   :caption: :file:`test-sync-2.py`
   :emphasize-lines:  2,6-11
   :linenos:

   from mpi4py import MPI
   from mpi4py.util.sync import Counter, Mutex

   comm = MPI.COMM_WORLD

   mutex = Mutex(comm)
   counter = Counter(comm)
   with mutex:
      value = next(counter)
   counter.free()
   mutex.free()

   assert (
      list(range(comm.size)) ==
      sorted(comm.allgather(value))
   )


.. Local variables:
.. fill-column: 79
.. End:
