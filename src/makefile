PYTHON_DIR=/usr/local
PYTHON_VER=2.5

all: /tmp/MPI.so

PYTHON_INCDIR=${PYTHON_DIR}/include/python${PYTHON_VER}
PYTHON_LIBDIR=${PYTHON_DIR}/lib
PYTHON_LIB=python${PYTHON_VER}



MPI.c: mpi4py/MPI.pyx $(wildcard mpi4py/*.pxd) $(wildcard mpi4py/*.pyx) $(wildcard mpi4py/*.pxi)
	cython --cleanup 9 -I. $< -o $@
#	cp $@ $@.orig; ../cycompact $@; mv $@.sub $@

MPI_DIR    = /usr/local/mpich2/1.0.6
MPI_LIBDIR = ${MPI_DIR}/lib
MPICC      = ${MPI_DIR}/bin/mpicc

OPT = -O3 -fno-strict-aliasing
WARN = -Wall -pedantic -Wno-long-long
COMPILER = ${MPICC} ${OPT} ${WARN} -fPIC -shared \
	-I${PYTHON_INCDIR} -L${PYTHON_LIBDIR} -Wl,-rpath,${PYTHON_LIBDIR} -l${PYTHON_LIB} \
	-Wl,-rpath,${MPI_LIBDIR}

/tmp/MPI.so: MPI.c
	${COMPILER} $< -o $@


srcfix: MPI.c
	mv MPI.c MPI.c.tmp
	echo '/* -*- fundamental -*- */' > MPI.c
	cat MPI.c.tmp >> MPI.c
	rm MPI.c.tmp
