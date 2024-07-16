mpi4py.util.pkl5
----------------

.. module:: mpi4py.util.pkl5
   :synopsis: Pickle-based communication using protocol 5.

.. versionadded:: 3.1.0

:mod:`pickle` protocol 5 (see :pep:`574`) introduced support for out-of-band
buffers, allowing for more efficient handling of certain object types with
large memory footprints.

MPI for Python uses the traditional in-band handling of buffers. This approach
is appropriate for communicating non-buffer Python objects, or buffer-like
objects with small memory footprints. For point-to-point communication, in-band
buffer handling allows for the communication of a pickled stream with a single
MPI message, at the expense of additional CPU and memory overhead in the
pickling and unpickling steps.

The :mod:`mpi4py.util.pkl5` module provides communicator wrapper classes
reimplementing pickle-based point-to-point and collective communication methods
using pickle protocol 5. Handling out-of-band buffers necessarily involves
multiple MPI messages, thus increasing latency and hurting performance in case
of small size data. However, in case of large size data, the zero-copy savings
of out-of-band buffer handling more than offset the extra latency costs.
Additionally, these wrapper methods overcome the infamous 2 GiB message count
limit (MPI-1 to MPI-3).

.. note::

   Support for pickle protocol 5 is available in the :mod:`pickle` module
   within the Python standard library since Python 3.8. Previous Python 3
   releases can use the :mod:`pickle5` backport, which is available on `PyPI
   <pickle5-pypi_>`_ and can be installed with::

       python -m pip install pickle5

   .. _pickle5-pypi: https://pypi.org/project/pickle5/


.. autoclass:: Request

   Custom request class for nonblocking communications.

   .. note:: :class:`Request` is not a subclass of :class:`mpi4py.MPI.Request`

   .. automethod:: Free

   .. automethod:: free

   .. automethod:: cancel

   .. automethod:: get_status

   .. automethod:: test

   .. automethod:: wait

   .. automethod:: get_status_all

      :classmethod:

   .. automethod:: testall

      :classmethod:

   .. automethod:: waitall

      :classmethod:


.. autoclass:: Message

   Custom message class for matching probes.

   .. note:: :class:`Message` is not a subclass of :class:`mpi4py.MPI.Message`

   .. automethod:: free

   .. automethod:: recv

   .. automethod:: irecv

   .. automethod:: probe

      :classmethod:

   .. automethod:: iprobe

      :classmethod:


.. autoclass:: Comm

   Base communicator wrapper class.

   .. automethod:: send

   .. automethod:: bsend

   .. automethod:: ssend

   .. automethod:: isend

   .. automethod:: ibsend

   .. automethod:: issend

   .. automethod:: recv

   .. automethod:: irecv

      .. warning:: This method cannot be supported reliably
                   and raises :exc:`RuntimeError`.

   .. automethod:: sendrecv

   .. automethod:: mprobe

   .. automethod:: improbe

   .. automethod:: bcast

      .. versionadded:: 3.1.0

   .. automethod:: gather

      .. versionadded:: 4.0.0

   .. automethod:: scatter

      .. versionadded:: 4.0.0

   .. automethod:: allgather

      .. versionadded:: 4.0.0

   .. automethod:: alltoall

      .. versionadded:: 4.0.0


.. autoclass:: Intracomm

   Intracommunicator wrapper class.


.. autoclass:: Intercomm

   Intercommunicator wrapper class.


Examples
++++++++

.. code-block:: python
   :name: test-pkl5-1
   :caption: :file:`test-pkl5-1.py`
   :emphasize-lines: 3,5,11
   :linenos:

   import numpy as np
   from mpi4py import MPI
   from mpi4py.util import pkl5

   comm = pkl5.Intracomm(MPI.COMM_WORLD)  # comm wrapper
   size = comm.Get_size()
   rank = comm.Get_rank()
   dst = (rank + 1) % size
   src = (rank - 1) % size

   sobj = np.full(1024**3, rank, dtype='i4')  # > 4 GiB
   sreq = comm.isend(sobj, dst, tag=42)
   robj = comm.recv (None, src, tag=42)
   sreq.Free()

   assert np.min(robj) == src
   assert np.max(robj) == src

.. code-block:: python
   :name: test-pkl5-2
   :caption: :file:`test-pkl5-2.py`
   :emphasize-lines: 3,5,11
   :linenos:

   import numpy as np
   from mpi4py import MPI
   from mpi4py.util import pkl5

   comm = pkl5.Intracomm(MPI.COMM_WORLD)  # comm wrapper
   size = comm.Get_size()
   rank = comm.Get_rank()
   dst = (rank + 1) % size
   src = (rank - 1) % size

   sobj = np.full(1024**3, rank, dtype='i4')  # > 4 GiB
   sreq = comm.isend(sobj, dst, tag=42)

   status = MPI.Status()
   rmsg = comm.mprobe(status=status)
   assert status.Get_source() == src
   assert status.Get_tag() == 42
   rreq = rmsg.irecv()
   robj = rreq.wait()

   sreq.Free()
   assert np.max(robj) == src
   assert np.min(robj) == src


.. Local variables:
.. fill-column: 79
.. End:
