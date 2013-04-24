.PHONY: default
default: build test clean

PYTHON = python
PYTHON_CONFIG = ${PYTHON} ../python-config
MPI4PY_INCLUDE = ${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}


SWIG = swig
SWIG_PY = ${SWIG} -python
.PHONY: src
src: helloworld_wrap.c
helloworld_wrap.c: helloworld.i
	${SWIG_PY} -I${MPI4PY_INCLUDE} -o $@ $<

MPICC = mpicc
CFLAGS = -fPIC ${shell ${PYTHON_CONFIG} --includes}
LDFLAGS = -shared ${shell ${PYTHON_CONFIG} --libs}
SO = ${shell ${PYTHON_CONFIG} --extension-suffix}
.PHONY: build
build: _helloworld${SO}
_helloworld${SO}: helloworld_wrap.c
	${MPICC} ${CFLAGS} -I${MPI4PY_INCLUDE} -o $@ $< ${LDFLAGS}


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} helloworld_wrap.c helloworld.py* _helloworld${SO}
