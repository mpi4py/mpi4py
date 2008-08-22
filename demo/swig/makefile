.PHONY: all src ext test clean

PYTHON  = python
SWIG    = swig -python
MPICC   = mpicc 
MPIEXEC = mpiexec

PYTHON_INCLUDE = ${shell ${PYTHON} -c 'from distutils import sysconfig; print( sysconfig.get_python_inc() )'}
MPI4PY_INCLUDE = ${shell ${PYTHON} -c 'import mpi4py; print( mpi4py.get_include() )'}

CFLAGS = -shared -fPIC
SO = .so
NP = -n 5

all: test

src: _helloworld.c
ext: _helloworld${SO}
test: ext
	${MPIEXEC} ${NP} ${PYTHON} -c 'from mpi4py import MPI; import helloworld as hw; hw.hello(MPI.COMM_WORLD)'

clean:
	${RM} helloworld.py* _helloworld${SO} _helloworld.c 


_helloworld.c: helloworld.i
	${SWIG} -I${MPI4PY_INCLUDE} -o $@ $< 
_helloworld${SO}: _helloworld.c
	${MPICC} ${CFLAGS} -I${PYTHON_INCLUDE} -I${MPI4PY_INCLUDE} -o $@ $<
