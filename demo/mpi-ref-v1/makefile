.PHONY: default build test clean test_seq test_mpi

default: build test clean

build:

PYTHON  = python
MPIEXEC = mpiexec
NP_FLAG = -n
NP      = 3

test_seq:
	${MAKE} MPIEXEC= NP_FLAG= NP= test_mpi

test_mpi:
	-@for i in `ls ex-*.py`; do \
	    echo ${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} $$i; \
	    ${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} $$i; \
	done

test: test_seq test_mpi

clean:
