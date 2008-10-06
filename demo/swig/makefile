.PHONY: default all src build test clean

PYTHON = python
PYTHON_INCLUDE = ${shell ${PYTHON} -c 'from distutils import sysconfig; print( sysconfig.get_python_inc() )'}
MPI4PY_INCLUDE = ${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}


default: build
all: test


SWIG = swig
SWIG_PY = ${SWIG} -python
src: _helloworld.c
_helloworld.c: helloworld.i
	${SWIG_PY} -I${MPI4PY_INCLUDE} -o $@ $< 


MPICC  = mpicc 
CFLAGS = -shared -fPIC
SO = .so
build: _helloworld${SO}
_helloworld${SO}: _helloworld.c
	${MPICC} ${CFLAGS} -I${PYTHON_INCLUDE} -I${MPI4PY_INCLUDE} -o $@ $<


MPIEXEC = mpiexec
NP = -n 5
test: build
	${MPIEXEC} ${NP} ${PYTHON} test.py


clean:
	${RM} helloworld.py* _helloworld${SO} _helloworld.c
