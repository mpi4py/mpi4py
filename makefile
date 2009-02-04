.PHONY: default src \
	config build test install \
	clean distclean srcclean fullclean uninstall \
	cython epydoc sdist

PYTHON = python

default: build

src: src/MPI.c

config: 
	${PYTHON} setup.py config ${CONFIGOPT}

build: src
	${PYTHON} setup.py build ${BUILDOPT}

test:
	${MPIEXEC} ${VALGRIND} ${PYTHON} test/runalltest.py < /dev/null

install: build
	${PYTHON} setup.py install ${INSTALLOPT} --home=${HOME}

clean:
	${PYTHON} setup.py clean --all
	-${RM} _configtest.* *.py[co]

distclean: clean 
	-${RM} -r build  *.py[co]
	-${RM} -r MANIFEST dist mpi4py.egg-info
	-${RM} `find . -name '*~'`
	-${RM} `find . -name '*.py[co]'`

srcclean:
	${RM} src/mpi4py_MPI.c
	${RM} src/include/mpi4py/mpi4py_MPI.h
	${RM} src/include/mpi4py/mpi4py_MPI_api.h

fullclean: distclean srcclean

uninstall:
	-${RM} -r ${HOME}/lib/python/mpi4py
	-${RM} -r ${HOME}/lib/python/mpi4py-*-py*.egg-info

CY_SRC_PXD = $(wildcard src/include/mpi4py/*.pxd)
CY_SRC_PXI = $(wildcard src/MPI/*.pxi) $(wildcard src/include/mpi4py/*.pxi)
CY_SRC_PYX = $(wildcard src/MPI/*.pyx)
src/MPI.c: src/mpi4py_MPI.c
src/mpi4py_MPI.c: ${CY_SRC_PXD} ${CY_SRC_PXI} ${CY_SRC_PYX}
	${PYTHON} ./conf/cythonize.py

cython:
	${PYTHON} ./conf/cythonize.py

epydoc:
	${PYTHON} ./conf/epydocify.py -o /tmp/mpi4py-api-doc

sdist: src
	${PYTHON} setup.py sdist ${SDISTOPT}
