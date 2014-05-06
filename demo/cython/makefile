.PHONY: default
default: build test clean

PYTHON = python
PYTHON_CONFIG = ${PYTHON} ../python-config
MPI4PY_INCLUDE = -I${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}

CYTHON = cython
.PHONY: src
src: helloworld.c
helloworld.c: helloworld.pyx
	${CYTHON} ${MPI4PY_INCLUDE} $<


MPICC = mpicc
CFLAGS = -fPIC ${shell ${PYTHON_CONFIG} --includes}
LDFLAGS = -shared ${shell ${PYTHON_CONFIG} --libs}
SO = ${shell ${PYTHON_CONFIG} --extension-suffix}
.PHONY: build
build: helloworld${SO}
helloworld${SO}: helloworld.c
	${MPICC} ${CFLAGS} ${MPI4PY_INCLUDE} -o $@ $< ${LDFLAGS}


.PHONY: test
test: build
	${PYTHON} -c 'import helloworld'


.PHONY: clean
clean:
	${RM} helloworld.c helloworld${SO}
