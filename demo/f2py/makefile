.PHONY: default all build test clean

PYTHON  = python


default: build
all: test


F2PY = f2py --fcompiler=gnu95
MPIF90 = mpif90
SO = .so
build: helloworld${SO}
helloworld${SO}: helloworld.f90
	${F2PY} --f90exec=${MPIF90} -m helloworld -c $<


MPIEXEC = mpiexec
NP = -n 5
test: build
	${MPIEXEC} ${NP} ${PYTHON} test.py


clean:
	${RM} helloworld${SO}
