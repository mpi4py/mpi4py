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


.PHONY: test
test: build
	${PYTHON} -c 'import helloworld'


.PHONY: clean
clean:
	${RM} helloworld.c helloworld${SO}
