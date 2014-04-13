.PHONY: default
default: build test clean

PYTHON = python
PYTHON_CONFIG = ${PYTHON} ../python-config
MPI4PY_INCLUDE = ${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}
BOOST_INCS = 
BOOST_LIBS = -lboost_python


MPICXX = mpicxx
CXXFLAGS = -fPIC ${shell ${PYTHON_CONFIG} --includes} ${BOOST_INCS}
LDFLAGS = -shared ${shell ${PYTHON_CONFIG} --libs} ${BOOST_LIBS}
SO = ${shell ${PYTHON_CONFIG} --extension-suffix}
.PHONY: build
build: helloworld${SO}
helloworld${SO}: helloworld.cxx
	${MPICXX} ${CXXFLAGS} -I${MPI4PY_INCLUDE} -o $@ $< ${LDFLAGS}


MPIEXEC = mpiexec
NP_FLAG = -n
NP = 5
.PHONY: test
test: build
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test.py


.PHONY: clean
clean:
	${RM} helloworld${SO}
