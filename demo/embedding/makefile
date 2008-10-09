.PHONY: build test clean

PYTHON = python
PYTHON_PERFIX = ${shell ${PYTHON} -c 'import sys; print(sys.exec_prefix)'}/bin
PYTHON_CONFIG = ${PYTHON_PERFIX}/python-config

MPICC   = mpicc
CFLAGS  = ${shell ${PYTHON_CONFIG} --cflags}
LDFLAGS = ${shell ${PYTHON_CONFIG} --ldflags}
LDLAST  = -Xlinker -export-dynamic
build: helloworld
helloworld: helloworld.c
	${MPICC} ${CFLAGS} ${LDFLAGS} ${LDLAST} -o $@ $<


MPIEXEC = mpiexec
NP = -n 5
test: build
	${MPIEXEC} ${NP} ./helloworld


clean:
	${RM} helloworld
