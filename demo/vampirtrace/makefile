MPIEXEC = mpiexec
PYTHON = python
N = 8

.PHONY: default
default: build test clean


.PHONY: run-cpilog run-ring run-threads run
run:    run-cpilog run-ring run-threads
run-cpilog:
	${MPIEXEC} -n ${N} ${PYTHON} cpilog.py
run-ring:
	${MPIEXEC} -n ${N} ${PYTHON} ring.py
run-threads:
	${MPIEXEC} -n ${N} ${PYTHON} threads.py

.PHONY: view-cpilog view-ring view-threads view
view:   view-cpilog view-ring view-threads
view-cpilog:  cpilog.otf
view-ring:    ring.otf
view-threads: threads.otf

cpilog.otf:  run-cpilog
ring.otf:    run-ring
threads.otf: run-threads

.PHONY: build
build:

.PHONY: test
test: run

.PHONY: clean
clean:
	${RM} *.otf *.uctl *.*.def.z *.*.events.z *.*.marker.z
