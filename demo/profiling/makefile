MPIEXEC = mpiexec
N = 8

PYTHON = python$(py)

.PHONY: default
default: build test clean


.PHONY: run-cpi run-ring run-threads run
run:    run-cpi run-ring run-threads
run-cpi:
	${MPIEXEC} -n ${N} ${PYTHON} cpi.py
run-ring:
	${MPIEXEC} -n ${N} ${PYTHON} ring.py
run-threads:
	${MPIEXEC} -n ${N} ${PYTHON} threads.py

.PHONY: build
build:

.PHONY: test
test: run

.PHONY: clean
clean:
