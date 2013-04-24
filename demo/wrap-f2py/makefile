.PHONY: default
default: build test clean

PYTHON  = python
PYTHON_CONFIG = ${PYTHON} ../python-config


MPIF90 = mpif90
F2PY = f2py --fcompiler=gnu95
SO = ${shell ${PYTHON_CONFIG} --extension-suffix}
.PHONY: build
build: helloworld${SO}
helloworld${SO}: helloworld.f90
	${F2PY} --f90exec=${MPIF90} -m helloworld -c $<


MPIEXEC = mpiexec
NP_FLAG = -n
NP = -n 5
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} helloworld${SO}
