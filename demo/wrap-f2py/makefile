include ../config.mk
.PHONY: default build test clean
default: build test clean

MODULE = helloworld
SOURCE = $(MODULE).f90
TARGET = $(MODULE)$(EXT_SUFFIX)

ldflags :=
ifndef ldflags # mpich
ldflags := $(shell $(MPIFORT) -link-info 2> /dev/null)
endif
ifndef ldflags # openmpi
ldflags := $(shell $(MPIFORT) -show:link 2> /dev/null)
endif
export FC=$(MPIFORT)
export LDFLAGS=$(wordlist 2,$(words $(ldflags)),$(ldflags))

$(TARGET): $(SOURCE)
	$(F2PY) -m $(MODULE) -c $<


build: $(TARGET)

test: build
	$(MPIEXEC_PYTHON) test.py

clean:
	$(RM) -r $(TARGET) __pycache__
