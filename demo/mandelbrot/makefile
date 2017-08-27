.PHONY: default build test clean

default: build test clean

build: mandelbrot-worker.exe

MPIF90=mpif90
FFLAGS= -O3
ifneq (${MPI_FORTRAN_MOD_DIR},)
FFLAGS += -I${MPI_FORTRAN_MOD_DIR}
endif
mandelbrot-worker.exe: mandelbrot-worker.f90
	${MPIF90} ${FFLAGS} -o $@ $<

PYTHON=python
MPIEXEC=mpiexec
NP_FLAG=-n

test: build
	${MPIEXEC} ${NP_FLAG} 1 ${PYTHON} mandelbrot-master.py
	${MPIEXEC} ${NP_FLAG} 7 ${PYTHON} mandelbrot.py
	${PYTHON} mandelbrot-seq.py

clean:
	${RM} mandelbrot-worker.exe
