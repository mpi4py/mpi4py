.PHONY: default
default: build test clean

PYTHON = python

MPICC = mpicc
LIBNAME = libhelloworld.so
.PHONY: build
build: ${LIBNAME}
${LIBNAME}: helloworld.c
	${MPICC} -shared -o $@ $<


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} -r ${LIBNAME} *.pyc __pycache__
