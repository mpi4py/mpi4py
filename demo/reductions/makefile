include ../config.mk
.PHONY: default build test clean
default: build test clean

build:

test:
	$(MPIEXEC_PYTHON) test_reductions.py -q

clean:
	$(RM) -r __pycache__
