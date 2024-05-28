include ../config.mk
.PHONY: default build test clean
default: build test clean

MODULE = helloworld
SOURCE = $(MODULE).cxx
TARGET = $(MODULE)$(EXT_SUFFIX)

CXX_FLAGS += -std=c++11
CXX_FLAGS += $(PYBIND11_INCLUDE)
CXX_FLAGS += $(MPI4PY_INCLUDE)
$(TARGET): $(SOURCE)
	$(MPICXX) $(CXX_FLAGS_SHARED) -o $@ $<

build: $(TARGET)

test: build
	$(MPIEXEC_PYTHON) test.py

clean:
	$(RM) -r $(TARGET) __pycache__
