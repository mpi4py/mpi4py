.PHONY: default
default: build test clean

PYTHON = python
PYTHON_CONFIG = ${PYTHON} ../python-config


CYTHON = cython
.PHONY: src
src: helloworld.c
helloworld.c: helloworld.pyx
	${CYTHON} $<


MPICC = mpicc
CFLAGS = -fPIC ${shell ${PYTHON_CONFIG} --includes}
LDFLAGS = -shared ${shell ${PYTHON_CONFIG} --libs}
SO = ${shell ${PYTHON_CONFIG} --extension-suffix}
.PHONY: build
build: helloworld${SO}
helloworld${SO}: helloworld.c
	${MPICC} ${CFLAGS} -o $@ $< ${LDFLAGS}


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} helloworld.c helloworld${SO}
