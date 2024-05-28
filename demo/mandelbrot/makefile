include ../config.mk
.PHONY: default build test clean
default: build test clean

PROGRAM = mandelbrot-worker
SOURCE = $(PROGRAM).f90
TARGET = $(PROGRAM).exe

FCFLAGS = -O3
$(TARGET): $(SOURCE)
	$(MPIFORT) $(FCFLAGS) -o $@ $<

build: $(TARGET)

test: build
	$(MPIEXEC) $(NP_FLAG) 1 $(PYTHON) mandelbrot-master.py
	$(MPIEXEC) $(NP_FLAG) 7 $(PYTHON) mandelbrot.py
	$(PYTHON) mandelbrot-seq.py

clean:
	$(RM) $(TARGET) __pycache__
