include ../config.mk
.PHONY: default build test clean
default: build test clean

LIBRARY = helloworld
SOURCE = $(LIBRARY).f08
TARGET = lib$(LIBRARY)$(LIB_SUFFIX)

ifneq ($(MPI_FORTRAN_MOD_DIR),)
FCFLAGS += -I$(MPI_FORTRAN_MOD_DIR)
endif
$(TARGET): $(SOURCE)
	$(MPIFORT) $(FC_FLAGS_SHARED) -o $@ $<

build: $(TARGET)

test: build
	$(MPIEXEC_PYTHON) test.py

clean:
	$(RM) -r $(TARGET) __pycache__
