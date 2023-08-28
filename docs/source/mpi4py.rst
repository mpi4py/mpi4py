mpi4py
======

.. automodule:: mpi4py
   :synopsis: The MPI for Python package.


Runtime configuration options
-----------------------------

.. data:: mpi4py.rc

   This object has attributes exposing runtime configuration options that
   become effective at import time of the :mod:`~mpi4py.MPI` module.

.. rubric:: Attributes Summary

.. table::
   :widths: grid

   ==============  ========================================================
   `initialize`    Automatic MPI initialization at import
   `threads`       Request initialization with thread support
   `thread_level`  Level of thread support to request
   `finalize`      Automatic MPI finalization at exit
   `fast_reduce`   Use tree-based reductions for objects
   `recv_mprobe`   Use matched probes to receive objects
   `irecv_bufsz`   Default buffer size in bytes for :meth:`~MPI.Comm.irecv`
   `errors`        Error handling policy
   ==============  ========================================================

.. rubric:: Attributes Documentation

.. attribute:: mpi4py.rc.initialize

   Automatic MPI initialization at import.

   :type: :class:`bool`
   :default: :obj:`True`

   .. seealso:: :envvar:`MPI4PY_RC_INITIALIZE`

.. attribute:: mpi4py.rc.threads

   Request initialization with thread support.

   :type: :class:`bool`
   :default: :obj:`True`

   .. seealso:: :envvar:`MPI4PY_RC_THREADS`

.. attribute:: mpi4py.rc.thread_level

   Level of thread support to request.

   :type: :class:`str`
   :default: ``"multiple"``
   :choices: ``"multiple"``, ``"serialized"``, ``"funneled"``, ``"single"``

   .. seealso:: :envvar:`MPI4PY_RC_THREAD_LEVEL`

.. attribute:: mpi4py.rc.finalize

   Automatic MPI finalization at exit.

   :type: :obj:`None` or :class:`bool`
   :default: :obj:`None`

   .. seealso:: :envvar:`MPI4PY_RC_FINALIZE`

.. attribute:: mpi4py.rc.fast_reduce

   Use tree-based reductions for objects.

   :type: :class:`bool`
   :default: :obj:`True`

   .. seealso:: :envvar:`MPI4PY_RC_FAST_REDUCE`

.. attribute:: mpi4py.rc.recv_mprobe

   Use matched probes to receive objects.

   :type: :class:`bool`
   :default: :obj:`True`

   .. seealso:: :envvar:`MPI4PY_RC_RECV_MPROBE`

.. attribute:: mpi4py.rc.irecv_bufsz

   Default buffer size in bytes for :meth:`~MPI.Comm.irecv`.

   :type: :class:`int`
   :default: ``32768``

   .. seealso:: :envvar:`MPI4PY_RC_IRECV_BUFSZ`
   .. versionadded:: 4.0.0

.. attribute:: mpi4py.rc.errors

   Error handling policy.

   :type: :class:`str`
   :default: ``"exception"``
   :choices: ``"exception"``, ``"default"``, ``"abort"``, ``"fatal"``

   .. seealso:: :envvar:`MPI4PY_RC_ERRORS`


.. rubric:: Example

MPI for Python features automatic initialization and finalization of the MPI
execution environment. By using the `mpi4py.rc` object, MPI initialization and
finalization can be handled programmatically::

  import mpi4py
  mpi4py.rc.initialize = False  # do not initialize MPI automatically
  mpi4py.rc.finalize = False    # do not finalize MPI automatically

  from mpi4py import MPI # import the 'MPI' module

  MPI.Init()      # manual initialization of the MPI environment
  ...             # your finest code here ...
  MPI.Finalize()  # manual finalization of the MPI environment


Environment variables
---------------------

The following environment variables override the corresponding attributes of
the :data:`mpi4py.rc` and :data:`MPI.pickle` objects at import time of the
:mod:`~mpi4py.MPI` module.

.. note::

   For variables of boolean type, accepted values are ``0`` and ``1``
   (interpreted as :obj:`False` and :obj:`True`, respectively), and strings
   specifying a `YAML boolean`_ value (case-insensitive).

   .. _YAML boolean: https://yaml.org/type/bool.html

.. envvar:: MPI4PY_RC_INITIALIZE

  :type: :class:`bool`
  :default: :obj:`True`

  Whether to automatically initialize MPI at import time of the
  :mod:`mpi4py.MPI` module.

  .. seealso:: :attr:`mpi4py.rc.initialize`
  .. versionadded:: 4.0.0

.. envvar:: MPI4PY_RC_FINALIZE

  :type:  :obj:`None` | :class:`bool`
  :default: :obj:`None`
  :choices: :obj:`None`, :obj:`True`, :obj:`False`

  Whether to automatically finalize MPI at exit time of the Python process.

  .. seealso:: :attr:`mpi4py.rc.finalize`
  .. versionadded:: 4.0.0

.. envvar:: MPI4PY_RC_THREADS

  :type: :class:`bool`
  :default: :obj:`True`

  Whether to initialize MPI with thread support.

  .. seealso:: :attr:`mpi4py.rc.threads`
  .. versionadded:: 3.1.0

.. envvar:: MPI4PY_RC_THREAD_LEVEL

  :default: ``"multiple"``
  :choices: ``"single"``, ``"funneled"``,
            ``"serialized"``, ``"multiple"``

  The level of required thread support.

  .. seealso:: :attr:`mpi4py.rc.thread_level`
  .. versionadded:: 3.1.0

.. envvar:: MPI4PY_RC_FAST_REDUCE

  :type: :class:`bool`
  :default: :obj:`True`

  Whether to use tree-based reductions for objects.

  .. seealso:: :attr:`mpi4py.rc.fast_reduce`
  .. versionadded:: 3.1.0

.. envvar:: MPI4PY_RC_RECV_MPROBE

  :type: :class:`bool`
  :default: :obj:`True`

  Whether to use matched probes to receive objects.

  .. seealso:: :attr:`mpi4py.rc.recv_mprobe`

.. envvar:: MPI4PY_RC_IRECV_BUFSZ

  :type: :class:`bool`
  :default: :obj:`True`

  Default buffer size in bytes for :meth:`~MPI.Comm.irecv`.

  .. seealso:: :attr:`mpi4py.rc.irecv_bufsz`
  .. versionadded:: 4.0.0

.. envvar:: MPI4PY_RC_ERRORS

  :default: ``"exception"``
  :choices: ``"exception"``, ``"default"``, ``"abort"``, ``"fatal"``

  Controls default MPI error handling policy.

  .. seealso:: :attr:`mpi4py.rc.errors`
  .. versionadded:: 3.1.0

.. envvar:: MPI4PY_PICKLE_PROTOCOL

  :type: :class:`int`
  :default: :data:`pickle.HIGHEST_PROTOCOL`

  Controls the default pickle protocol to use when communicating Python
  objects.

  .. seealso:: :attr:`~mpi4py.MPI.Pickle.PROTOCOL` attribute of the
               :data:`MPI.pickle` object within the :mod:`~mpi4py.MPI` module.
  .. versionadded:: 3.1.0

.. envvar:: MPI4PY_PICKLE_THRESHOLD

  :type: :class:`int`
  :default: ``262144``

  Controls the default buffer size threshold for switching from in-band to
  out-of-band buffer handling when using pickle protocol version 5 or higher.

  .. seealso:: :attr:`~mpi4py.MPI.Pickle.THRESHOLD` attribute of the
               :data:`MPI.pickle` object within the :mod:`~mpi4py.MPI` module.
  .. versionadded:: 3.1.2


Miscellaneous functions
-----------------------

.. autofunction:: mpi4py.profile

.. autofunction:: mpi4py.get_config

.. autofunction:: mpi4py.get_include


.. Local variables:
.. fill-column: 79
.. End:
