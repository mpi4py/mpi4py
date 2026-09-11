include ../config.mk
.PHONY: default build test clean
default: build test clean

build:

test:
	$(PYTHON) sendrecv.py
	$(MPIEXEC_PYTHON) issue784.py

clean:
