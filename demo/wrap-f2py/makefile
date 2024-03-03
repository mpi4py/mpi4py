.PHONY: default
default: build test clean

PYTHON = python$(py)
PYTHON_CONFIG = ${PYTHON} ../python-config


MPIFORT = mpifort
F2PY = f2py

ldflags :=
ifndef ldflags # mpich
ldflags := $(shell $(MPIFORT) -link-info 2> /dev/null)
endif
ifndef ldflags # openmpi
ldflags := $(shell $(MPIFORT) -show:link 2> /dev/null)
endif
export FC=$(MPIFORT)
export LDFLAGS=$(wordlist 2,$(words $(ldflags)),$(ldflags))
SO = ${shell ${PYTHON_CONFIG} --extension-suffix}

.PHONY: build
build: helloworld${SO}
helloworld${SO}: helloworld.f90
	${F2PY} -m helloworld -c $<


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} helloworld${SO}
