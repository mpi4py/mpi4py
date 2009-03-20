.PHONY: default src build test clean

default: build test clean

PYTHON = python

PYTHON_INCLUDE = ${shell ${PYTHON} -c 'from distutils import sysconfig; print( sysconfig.get_python_inc() )'}
MPI4PY_INCLUDE = ${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}

CYTHON = cython
src: helloworld.c
helloworld.c: helloworld.pyx
	${CYTHON} -I${MPI4PY_INCLUDE} $<


MPICC = mpicc -shared -fPIC
CFLAGS = -shared -fPIC
SO = ${shell ${PYTHON} -c 'import imp; print (imp.get_suffixes()[0][0])'}
build: helloworld${SO}
helloworld${SO}: helloworld.c
	${MPICC} ${CFLAGS} -I${PYTHON_INCLUDE} -I${MPI4PY_INCLUDE} -o $@ $<


test: build
	${PYTHON} -c 'import helloworld'


clean:
	${RM} helloworld.c helloworld${SO}
