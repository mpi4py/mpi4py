.PHONY: default
default: build test clean

PYTHON = python

.PHONY: build
build: libmpi.h libmpi.c
	${PYTHON} libmpi.py

libmpi.h:
	${PYTHON} apigen.py
libmpi.c: libmpi.h

MPIEXEC = mpiexec
NP_FLAG = -n
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} 5 ${PYTHON} test_helloworld.py
	${MPIEXEC} ${NP_FLAG} 4 ${PYTHON} test_ringtest.py
	${MPIEXEC} ${NP_FLAG} 2 ${PYTHON} test_latency.py

.PHONY: clean
clean:
	${RM} -r libmpi.h libmpi.c
	${RM} -r *py[co] __pycache__
