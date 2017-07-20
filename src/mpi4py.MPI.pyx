#cython: embedsignature=True
#cython: cdivision=True
#cython: binding=False
#cython: auto_pickle=False
#cython: always_allow_keywords=True
#cython: allow_none_for_extension_args=False
#cython: autotestdict=False
#cython: warn.multiple_declarators=False
#cython: optimize.use_switch=False
from __future__ import absolute_import
cimport cython
include "mpi4py/MPI/MPI.pyx"
