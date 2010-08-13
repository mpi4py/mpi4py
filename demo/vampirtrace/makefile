MPIEXEC = mpiexec
PYTHON = python
N = 8

.PHONY: default
default: build test clean


.PHONY: run-cpilog run-ring run
run:    run-cpilog run-ring
run-cpilog:
	${MPIEXEC} -n ${N} ${PYTHON} cpilog.py
run-ring:
	${MPIEXEC} -n ${N} ${PYTHON} ring.py

.PHONY: view-cpilog view-ring view
view:   view-cpilog view-ring
view-cpilog: cpilog.otf
view-ring: ring.otf

cpilog.otf: run-cpilog
ring.otf: run-ring

.PHONY: build
build:

.PHONY: test
test: run

.PHONY: clean
clean:
	${RM} *.otf *.uctl *.*.def.z *.*.events.z
