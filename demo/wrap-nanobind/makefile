include ../config.mk
.PHONY: default build test clean
default: build test clean

MODULE = helloworld
SOURCE = $(MODULE).cxx
TARGET = $(MODULE)$(EXT_SUFFIX)

$(TARGET): $(SOURCE)
	cmake -S . -B build -DCMAKE_INSTALL_PREFIX=.
	cmake --build   build
	cmake --install build

build: $(TARGET)

test: build
	$(MPIEXEC_PYTHON) test.py

clean:
	$(RM) -r $(TARGET) __pycache__ build
