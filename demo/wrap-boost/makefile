include ../config.mk
.PHONY: default build test clean
default: build test clean

MODULE = helloworld
SOURCE = $(MODULE).cxx
TARGET = $(MODULE)$(EXT_SUFFIX)

BOOST_PYVER = $(shell $(PYTHON) -c 'import sys; print(*sys.version_info[:2], sep="")')
BOOST_INCLUDE =
BOOST_LDFLAGS = -lboost_python$(BOOST_PYVER)

PYCCFLAGS += $(BOOST_INCLUDE)
PYLDFLAGS += $(BOOST_LDFLAGS)
$(TARGET): $(SOURCE)
	$(MPICXX) $(MPI4PY_INCLUDE) $(CXX_FLAGS_SHARED) -o $@ $<

build: $(TARGET)

test: build
	$(MPIEXEC_PYTHON) test.py

clean:
	$(RM) -r $(TARGET) __pycache__
