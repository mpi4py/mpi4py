.PHONY: default config src build test install uninstall sdist clean distclean fullclean

PYTHON = python

default: build

config: 
	${PYTHON} setup.py config ${CONFIGOPT}

src: src/MPI.c

build: src
	${PYTHON} setup.py build ${BUILDOPT}

test:
	${MPIEXEC} ${PYTHON} test/runalltest.py < /dev/null

install: build
	${PYTHON} setup.py install ${INSTALLOPT} --home=${HOME}

uninstall:
	-${RM} -r ${HOME}/lib/python/mpi4py
	-${RM} -r ${HOME}/lib/python/mpi4py-*-py*.egg-info

sdist: src
	${PYTHON} setup.py sdist ${SDISTOPT}


clean:
	${PYTHON} setup.py clean --all
	-${RM} _configtest.* *.py[co]
	-${MAKE} -C docs clean

distclean: clean 
	-${RM} -r build  *.py[co]
	-${RM} -r MANIFEST dist mpi4py.egg-info
	-${MAKE} -C docs distclean
	-${RM} `find . -name '*~'`
	-${RM} `find . -name '*.py[co]'`

fullclean: distclean
	${RM} src/mpi4py_MPI.c
	${RM} src/include/mpi4py/mpi4py_MPI.h
	${RM} src/include/mpi4py/mpi4py_MPI_api.h


CYTHON = cython
CYTHON_FLAGS = --cleanup 9
CYTHON_INCLUDE = -I. -Iinclude -Iinclude/mpi4py
CY_SRC_PXD = $(wildcard src/include/mpi4py/*.pxd)
CY_SRC_PXI = $(wildcard src/MPI/*.pxi) $(wildcard src/include/mpi4py/*.pxi)
CY_SRC_PYX = $(wildcard src/MPI/*.pyx)
src/MPI.c: src/mpi4py_MPI.c
src/mpi4py_MPI.c: ${CY_SRC_PXD} ${CY_SRC_PXI} ${CY_SRC_PYX}
	${CYTHON} ${CYTHON_FLAGS} ${CYTHON_INCLUDE} -w src mpi4py.MPI.pyx -o mpi4py_MPI.c
	mv src/mpi4py_MPI.h src/mpi4py_MPI_api.h src/include/mpi4py
