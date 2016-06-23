#cython: embedsignature=True
#cython: cdivision=True
#cython: always_allow_keywords=True
#cython: autotestdict=False
#cython: warn.multiple_declarators=False
#cython: optimize.use_switch=False
cimport cython
include "mpi4py/MPI/MPI.pyx"
