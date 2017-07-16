.PHONY: default
default: build test clean

PYTHON  = python
PYTHON_CONFIG = ${PYTHON} ../python-config


SO = ${shell ${PYTHON_CONFIG} --extension-suffix}
MPIF90 = mpif90
F2PY = f2py
ifneq (${MPI_FORTRAN_MOD_DIR},)
F2PYFLAGS += --f90flags=-I${MPI_FORTRAN_MOD_DIR}
endif
.PHONY: build
build: helloworld${SO}
helloworld${SO}: helloworld.f90
	${F2PY} ${F2PYFLAGS} --f90exec=${MPIF90} -m helloworld -c $<


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} helloworld${SO}
