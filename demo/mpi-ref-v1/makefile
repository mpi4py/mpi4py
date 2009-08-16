.PHONY: default build test clean test_seq test_mpi

default: build test clean

build:

PYTHON  = python
MPIEXEC = mpiexec
NP      = -n 3

test_seq:
	${MAKE} MPIEXEC= NP= test_mpi

test_mpi:
	-@for i in `ls ex-*.py`; do \
	    echo ${MPIEXEC} ${NP} ${PYTHON} $$i; \
	    ${MPIEXEC} ${NP} ${PYTHON} $$i; \
	done

test: test_seq test_mpi

clean:
