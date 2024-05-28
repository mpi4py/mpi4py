include ../config.mk
.PHONY: default build test clean
default: build test clean

NP = 8
.PHONY: run-cpi run-ring run-threads run
run:    run-cpi run-ring run-threads
run-cpi:
	$(MPIEXEC_PYTHON) cpi.py
run-ring:
	$(MPIEXEC_PYTHON) ring.py
run-threads:
	$(MPIEXEC_PYTHON) threads.py

build:

test: run

clean:
