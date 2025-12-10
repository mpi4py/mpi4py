mpi4py.typing
=============

.. module:: mpi4py.typing
   :synopsis: Typing support.

.. versionadded:: 4.0.0

This module provides :term:`type aliases <type alias>` used to add
:term:`type hints <type hint>` to the various functions and methods
within the :mod:`~mpi4py.MPI` module.

.. seealso::

   Module :mod:`typing`
      Documentation of the :mod:`typing` standard module.


.. currentmodule:: mpi4py.typing

.. rubric:: Types Summary

.. autosummary::
   SupportsBuffer
   SupportsDLPack
   SupportsCAI
   Buffer
   Bottom
   InPlace
   Aint
   Count
   Displ
   Offset
   TypeSpec
   BufSpec
   BufSpecB
   BufSpecV
   BufSpecW
   TargetSpec

.. rubric:: Types Documentation

.. autoclass:: SupportsBuffer

   .. automethod:: __buffer__

.. autoclass:: SupportsDLPack

   .. automethod:: __dlpack__
   .. automethod:: __dlpack_device__

.. autoclass:: SupportsCAI

   .. autoproperty:: __cuda_array_interface__

.. autotype:: Buffer
.. autotype:: Bottom
.. autotype:: InPlace
.. autotype:: Aint
.. autotype:: Count
.. autotype:: Displ
.. autotype:: Offset
.. autotype:: TypeSpec
.. autotype:: BufSpec
.. autotype:: BufSpecB
.. autotype:: BufSpecV
.. autotype:: BufSpecW
.. autotype:: TargetSpec

.. autodata:: S
.. autodata:: T
.. autodata:: U
.. autodata:: V


.. Local variables:
.. fill-column: 79
.. End:
