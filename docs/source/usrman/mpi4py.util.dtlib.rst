mpi4py.util.dtlib
-----------------

.. module:: mpi4py.util.dtlib
   :synopsis: Convert NumPy and MPI datatypes.

.. versionadded:: 3.1.0

The :mod:`mpi4py.util.dtlib` module provides converter routines between NumPy
and MPI datatypes.

.. function:: from_numpy_dtype(dtype: numpy.typing.DTypeLike) \
              -> mpi4py.MPI.Datatype

   Convert NumPy datatype to MPI datatype.

.. function:: to_numpy_dtype(datatype: mpi4py.MPI.Datatype) \
              -> numpy.dtype

   Convert MPI datatype to NumPy datatype.


.. Local variables:
.. fill-column: 79
.. End:
