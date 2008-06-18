.PHONY: all src ext test clean

PYTHON = python
CYTHON = cython
MPICC  = mpicc -shared -fPIC

PYTHON_INCLUDE = ${shell ${PYTHON} -c 'from distutils import sysconfig; print( sysconfig.get_python_inc() )'}
MPI4PY_INCLUDE = ${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}

SO = .so

all: test

src: helloworld.c
ext: helloworld${SO}
test: ext
	${PYTHON} -c 'import helloworld'

clean:
	${RM} helloworld.c helloworld${SO}


helloworld.c: helloworld.pyx
	${CYTHON} -I${MPI4PY_INCLUDE} $<
helloworld${SO}: helloworld.c
	${MPICC} -I${PYTHON_INCLUDE} -I${MPI4PY_INCLUDE} -o $@ $<
