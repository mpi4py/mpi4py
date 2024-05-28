include ../config.mk
.PHONY: default build test clean
default: test

build:

test:
	$(MPIEXEC_PYTHON) nxtval-threads.py
	$(MPIEXEC_PYTHON) nxtval-dynproc.py
	$(MPIEXEC_PYTHON) nxtval-onesided.py
	$(MPIEXEC_PYTHON) nxtval-scalable.py
	$(MPIEXEC_PYTHON) nxtval-mpi3.py

clean:
