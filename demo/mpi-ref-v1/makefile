include ../config.mk
.PHONY: default build test clean
default: build test clean

.PHONY: run_seq
run_seq:
	-@for i in `ls ex-*.py`; do \
	    echo $(PYTHON) $$i; \
	    $(PYTHON) $$i; \
	done

.PHONY: run_mpi
run_mpi:
	-@for i in `ls ex-*.py`; do \
	    echo $(MPIEXEC_PYTHON) $$i; \
	    $(MPIEXEC_PYTHON) $$i; \
	done

build:

test: run_seq run_mpi

clean:
