.PHONY: all seq mpi test clean distclean

PYTHON  = python
MPIEXEC = mpiexec
NP      = -n 3

all: seq


seq:
	${MAKE} MPIEXEC= NP= test

mpi:
	${MAKE} test

test:
	-@for i in `ls ex-*.py`; do \
	    echo; echo ${MPIEXEC} ${NP} ${PYTHON} $$i; \
	    ${MPIEXEC} ${NP} ${PYTHON} $$i; \
	done

clean:

distclean: clean
