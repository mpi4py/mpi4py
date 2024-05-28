include ../config.mk
.PHONY: default build test clean
default: build test clean

libmpi.h libmpi.c.in:
	$(PYTHON) apigen.py

build: libmpi.h libmpi.c.in
	$(PYTHON) build.py

NP = 2
test: build
	$(MPIEXEC_PYTHON) test_helloworld.py
	$(MPIEXEC_PYTHON) test_ringtest.py
	$(MPIEXEC_PYTHON) test_latency.py

clean:
	$(RM) -r libmpi.* __pycache__
