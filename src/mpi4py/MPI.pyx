#cython: language_level=3str
#cython: embedsignature=True
#cython: embedsignature.format=python
#cython: annotation_typing=False
#cython: cdivision=True
#cython: auto_pickle=False
#cython: always_allow_keywords=True
#cython: allow_none_for_extension_args=False
#cython: autotestdict=False
#cython: warn.multiple_declarators=False
#cython: optimize.use_switch=False
#cython: binding=True

from __future__ import annotations
cimport cython  # no-cython-lint

include "MPI/MPI.pyx"
