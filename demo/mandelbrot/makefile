.PHONY: default build test clean

default: build test clean

build: mandelbrot-worker.exe

MPIF90=mpif90
FFLAGS= -O3
mandelbrot-worker.exe: mandelbrot-worker.f90
	${MPIF90} ${FFLAGS} -o $@ $<

PYTHON=python
MPIEXEC=mpiexec
NPFLAG= -n

test: build
	${MPIEXEC} ${NPFLAG} 1 ${PYTHON} mandelbrot-master.py
	${MPIEXEC} ${NPFLAG} 7 ${PYTHON} mandelbrot.py
	${PYTHON} mandelbrot-seq.py

clean:
	${RM} mandelbrot-worker.exe
