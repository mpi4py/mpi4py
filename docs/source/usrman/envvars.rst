.. _environment:

Environment variables
=====================

Below we list the environment variables added since mpi4py v3.1.0. The environment
variables overwrite their corresponding Python attributes at import time of the ``MPI``
module.

.. envvar:: MPI4PY_RC_INITIALIZE

  Default: ``True``

  Whether to automatically initialize MPI at import time of the ``MPI`` module.
  Corresponds to ``mpi4py.rc.initialize``.

.. envvar:: MPI4PY_RC_FINALIZE

  Default: ``None``

  Whether to automatically finalize MPI at the exit time. Corresponds to
  ``mpi4py.rc.finalize``.

.. envvar:: MPI4PY_RC_THREADS

  Default: ``True``

  Whether to initialize MPI with thread support. Corresponds to ``mpi4py.rc.threads``.

.. envvar:: MPI4PY_RC_THREAD_LEVEL

  Default: ``"multiple"``

  The level of required thread support. Any of the following is accepted: ``"single"``,
  ``"funneled"``, ``"serialized"``, ``"multiple"``. Corresponds to ``mpi4py.rc.thread_level``.

.. envvar:: MPI4PY_RC_FAST_REDUCE

  Default: ``True``

  Whether to use tree-based reductions for objects. Corresponds to ``mpi4py.rc.fast_reduce``.

.. envvar:: MPI4PY_RC_RECV_MPROBE

  Default: ``True``

  Whether to use matched probes to receive objects. Corresponds to ``mpi4py.rc.recv_mprobe``.

.. envvar:: MPI4PY_RC_ERRORS

  Default: ``"exception"``

  Controls mpi4py's default MPI error handling policy. Any of the following is accepted:
  ``"exception"``, ``"default"``, ``"fatal"``. Corresponds to ``mpi4py.rc.errors``.

.. envvar:: MPI4PY_PICKLE_PROTOCOL

  Default: ``5``.

  Controls the default pickle protocol to use when communicating Python objects. Corresponds
  to ``MPI.pickle.PROTOCOL``.
