.PHONY: default
default: build test clean

PYTHON = python

.PHONY: build
build: libmpi.h libmpi.c.in
	$(PYTHON) build.py

libmpi.h libmpi.c.in:
	$(PYTHON) apigen.py

MPIEXEC = mpiexec
NP_FLAG = -n
.PHONY: test
test: build
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) test_helloworld.py
	$(MPIEXEC) $(NP_FLAG) 4 $(PYTHON) test_ringtest.py
	$(MPIEXEC) $(NP_FLAG) 2 $(PYTHON) test_latency.py

.PHONY: clean
clean:
	$(RM) -r libmpi.*
	$(RM) -r *py[co] __pycache__
