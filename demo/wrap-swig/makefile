.PHONY: default
default: build test clean

PYTHON = python
PYTHON_INCLUDE = ${shell ${PYTHON} -c 'from distutils import sysconfig; print( sysconfig.get_python_inc() )'}
MPI4PY_INCLUDE = ${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}

SWIG = swig
SWIG_PY = ${SWIG} -python
.PHONY: src
src: helloworld_wrap.c
helloworld_wrap.c: helloworld.i
	${SWIG_PY} -I${MPI4PY_INCLUDE} -o $@ $<


MPICC  = mpicc
CFLAGS = -shared -fPIC
SO = ${shell ${PYTHON} -c 'import imp; print (imp.get_suffixes()[0][0])'}
.PHONY: build
build: _helloworld${SO}
_helloworld${SO}: helloworld_wrap.c
	${MPICC} ${CFLAGS} -I${PYTHON_INCLUDE} -I${MPI4PY_INCLUDE} -o $@ $<


MPIEXEC = mpiexec
NP = -n 5
.PHONY: test
test: build
	${MPIEXEC} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} helloworld_wrap.c helloworld.py* _helloworld${SO}
