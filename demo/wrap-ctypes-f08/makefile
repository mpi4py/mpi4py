.PHONY: default
default: build test clean

PYTHON = python$(py)

MPIFC = mpifort
ifneq ($(MPI_FORTRAN_MOD_DIR),)
FCFLAGS += -I$(MPI_FORTRAN_MOD_DIR)
endif

LIBNAME = libhelloworld.so
.PHONY: build
build: $(LIBNAME)
$(LIBNAME): helloworld.f08
	$(MPIFC) -shared -fPIC $(FCFLAGS) -o $@ $<


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
.PHONY: test
test: build
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test.py


.PHONY: clean
clean:
	$(RM) -r $(LIBNAME) *.pyc __pycache__
