include ../config.mk
.PHONY: default build test clean
default: build test clean

LIBRARY = helloworld
SOURCE = $(LIBRARY).c
TARGET = lib$(LIBRARY)$(LIB_SUFFIX)

$(TARGET): $(SOURCE)
	$(MPICC) $(CC_FLAGS_SHARED) -o $@ $<

build: $(TARGET)

test: build
	$(MPIEXEC_PYTHON) test.py

clean:
	$(RM) -r $(TARGET) __pycache__
