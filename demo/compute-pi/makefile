include ../config.mk
.PHONY: default build test clean
default: test

build:

test:
	echo 100 | $(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) cpi-cco.py
	echo 100 | $(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) cpi-rma.py
	echo 100 | $(MPIEXEC) $(NP_FLAG) 1     $(PYTHON) cpi-dpm.py $(NP)

clean:
