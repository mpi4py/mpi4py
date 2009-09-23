.PHONY: default build test clean

default: build test clean

PYTHON  = python

F2PY = f2py
F2PY_FC = --fcompiler=gnu95
MPIF90 = mpif90
SO = ${shell ${PYTHON} -c 'import imp; print (imp.get_suffixes()[0][0])'}
build: helloworld${SO}
helloworld${SO}: helloworld.f90
	${F2PY} ${F2PY_FC} --f90exec=${MPIF90} -m helloworld -c $<


MPIEXEC = mpiexec
NP = -n 5
test: build
	${MPIEXEC} ${NP} ${PYTHON} test.py


clean:
	${RM} helloworld${SO}
