MPIEXEC = mpiexec
PYTHON = python
N = 8

.PHONY: default
default: build test clean


.PHONY: run
run:
	${MPIEXEC} -n ${N} ${PYTHON} cpilog.py

cpilog.slog2: cpilog.clog2
	clog2TOslog2 $<
.PHONY: view
view: cpilog.slog2
	jumpshot $<



.PHONY: build
build: run cpilog.slog2

.PHONY: test
test:

.PHONY: clean
clean:
	${RM} *.[cs]log2
