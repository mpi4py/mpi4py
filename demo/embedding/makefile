.PHONY: default build test clean

default: build test clean

PYTHON = python
PYTHON_CONFIG = ${PYTHON} ../python-config

MPICC   = mpicc
CFLAGS  = ${shell ${PYTHON_CONFIG} --cflags}
LDFLAGS = ${shell ${PYTHON_CONFIG} --ldflags}
build: helloworld.exe
helloworld.exe: helloworld.c
	${MPICC} ${CFLAGS} -o $@ $< ${LDFLAGS}


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ./helloworld.exe


clean:
	${RM} -r helloworld.exe helloworld.exe.dSYM
