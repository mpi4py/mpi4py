.PHONY: default build test clean

default: build test clean

PYTHON = python
PYTHON_PERFIX = ${shell ${PYTHON} -c 'import sys; print(sys.exec_prefix)'}
PYTHON_VERSION = ${shell ${PYTHON} -c 'import sys; print(sys.version[:3])'}
PYTHON_CONFIG = ${PYTHON_PERFIX}/bin/python$(PYTHON_VERSION)-config

MPICC   = mpicc
CFLAGS  = ${shell ${PYTHON_CONFIG} --cflags}
LDFLAGS = ${shell ${PYTHON_CONFIG} --ldflags}
LDLAST  = -Xlinker -export-dynamic
build: helloworld.exe
helloworld.exe: helloworld.c
	${MPICC} ${CFLAGS} ${LDFLAGS} ${LDLAST} -o $@ $<


MPIEXEC = mpiexec
NP = -n 5
test: build
	${MPIEXEC} ${NP} ./helloworld.exe


clean:
	${RM} helloworld.exe
