.PHONY: default build test clean

default: build test clean

build: mandelbrot-worker.exe

MPIFORT = mpifort
FFLAGS = -O3
mandelbrot-worker.exe: mandelbrot-worker.f90
	${MPIFORT} ${FFLAGS} -o $@ $<

MPIEXEC = mpiexec
NP_FLAG = -n

PYTHON = python$(py)

test: build
	${MPIEXEC} ${NP_FLAG} 1 ${PYTHON} mandelbrot-master.py
	${MPIEXEC} ${NP_FLAG} 7 ${PYTHON} mandelbrot.py
	${PYTHON} mandelbrot-seq.py

clean:
	${RM} mandelbrot-worker.exe
