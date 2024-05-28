dir := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

PYTHON = python$(py)
PYTHON_CONFIG = $(PYTHON) $(dir)/python-config
PYBIND11_CONFIG = pybind11-config

PYTHON_INCLUDE   = $(shell $(PYTHON_CONFIG) --includes)
PYBIND11_INCLUDE = $(shell $(PYBIND11_CONFIG) --includes)
MPI4PY_INCLUDE   = -I$(shell $(PYTHON) -m mpi4py --prefix)/include

PYCCFLAGS = $(shell $(PYTHON_CONFIG) --cflags)
PYLDFLAGS = $(shell $(PYTHON_CONFIG) --ldflags)
CC_FLAGS  = $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) $(PYCCFLAGS) $(PYLDFLAGS)
CXX_FLAGS = $(CPPFLAGS) $(CXXFLAGS) $(LDFLAGS) $(PYCCFLAGS) $(PYLDFLAGS)
FC_FLAGS  = $(CPPFLAGS) $(FCFLAGS) $(LDFLAGS) $(PYLDFLAGS)
CC_SHARED = -fPIC
LD_SHARED = -shared

EXT_SUFFIX = $(shell ${PYTHON_CONFIG} --extension-suffix)
LIB_SUFFIX = $(suffix $(EXT_SUFFIX))

CYTHON = cython
F2PY = f2py
SWIG = swig

MPICC = mpicc
MPICXX = mpicxx
MPIFORT = mpifort

CC_FLAGS_SHARED  = $(CC_SHARED) $(LD_SHARED) $(CC_FLAGS)
CXX_FLAGS_SHARED = $(CC_SHARED) $(LD_SHARED) $(CXX_FLAGS)
FC_FLAGS_SHARED  = $(CC_SHARED) $(LD_SHARED) $(FC_FLAGS)


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
MPIEXEC_RUNCMD = $(MPIEXEC) $(MPIEXEC_FLAGS) $(NP_FLAG) $(NP)
MPIEXEC_PYTHON = $(MPIEXEC_RUNCMD) $(PYTHON)
