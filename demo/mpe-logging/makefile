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
view-cpilog: cpilog.slog2
	jumpshot $<
view-ring: ring.slog2
	jumpshot $<
view-threads: threads.slog2
	jumpshot $<

cpilog.clog2: run-cpilog
ring.clog2: run-ring
threads.clog2: run-threads
%.slog2: %.clog2
	clog2TOslog2 $<


.PHONY: build
build: run

.PHONY: test
test:

.PHONY: clean
clean:
	${RM} *.[cs]log2
