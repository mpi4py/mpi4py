include ../config.mk
.PHONY: default build test clean src
default: build test clean

MODULE = helloworld
SOURCE = $(MODULE).pyx
GENSRC = $(MODULE).c
TARGET = $(MODULE)$(EXT_SUFFIX)

$(GENSRC): $(SOURCE)
	$(CYTHON) $<
$(TARGET): $(GENSRC)
	$(MPICC) $(CC_FLAGS_SHARED) -o $@ $<

src:  $(GENSRC)

build: $(TARGET)

test: build
	$(MPIEXEC_PYTHON) test.py

clean:
	$(RM) -r $(TARGET) __pycache__ $(GENSRC)
