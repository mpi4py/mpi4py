mpi4py.util.pool
----------------

.. module:: mpi4py.util.pool
   :synopsis: :mod:`multiprocessing.pool` interface via :mod:`mpi4py.futures`.

.. versionadded:: 4.0.0

.. seealso::

   This module intends to be a drop-in replacement for the
   :mod:`multiprocessing.pool` interface from the Python standard library.
   The :class:`~mpi4py.util.pool.Pool` class exposed here is implemented as a
   thin wrapper around :class:`~mpi4py.futures.MPIPoolExecutor`.

.. note::

   The :mod:`mpi4py.futures` package offers a higher level interface
   for asynchronously pushing tasks to MPI worker process, allowing
   for a clear separation between submitting tasks and waiting for the
   results.


.. autoclass:: mpi4py.util.pool.Pool

   .. automethod:: __init__

   .. automethod:: apply

   .. automethod:: apply_async

   .. automethod:: map

   .. automethod:: map_async

   .. automethod:: imap

   .. automethod:: imap_unordered

   .. automethod:: starmap

   .. automethod:: starmap_async

   .. automethod:: istarmap

   .. automethod:: istarmap_unordered

   .. automethod:: close

   .. automethod:: terminate

   .. automethod:: join


.. autoclass:: mpi4py.util.pool.ThreadPool
   :show-inheritance:


.. autoclass:: mpi4py.util.pool.AsyncResult

   .. automethod:: get

   .. automethod:: wait

   .. automethod:: ready

   .. automethod:: successful


.. autoclass:: mpi4py.util.pool.ApplyResult
   :show-inheritance:


.. autoclass:: mpi4py.util.pool.MapResult
   :show-inheritance:
