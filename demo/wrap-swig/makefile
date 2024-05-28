include ../config.mk
.PHONY: default build test clean src
default: build test clean

MODULE = helloworld
SOURCE = $(MODULE).i
GENSRC = $(MODULE)_wrap.c
TARGET = _$(MODULE)$(EXT_SUFFIX)

$(GENSRC): $(SOURCE)
	$(SWIG) -python $(MPI4PY_INCLUDE) $<
$(TARGET): $(GENSRC)
	$(MPICC) $(MPI4PY_INCLUDE) $(CC_FLAGS_SHARED) -o $@ $<

src: $(GENSRC)

build: $(TARGET)

test: build
	$(MPIEXEC_PYTHON) test.py

clean:
	$(RM) -r $(TARGET) __pycache__ $(GENSRC) $(MODULE).py
