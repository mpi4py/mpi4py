.PHONY: default config src build test install uninstall sdist clean distclean fullclean

PYTHON = python
CYTHON = cython --cleanup 9

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
	${RM} src/MPI.c
	${RM} src/mpi4py/include/mpi4py/mpi4py_MPI.h
	${RM} src/mpi4py/include/mpi4py/mpi4py_MPI_api.h


src/MPI.c: src/mpi4py/MPI.pyx $(wildcard src/mpi4py/*.pxd) $(wildcard src/mpi4py/*.pyx) $(wildcard src/mpi4py/*.pxi)
	cd src && ${CYTHON} -Impi4py/include/mpi4py -I. mpi4py/MPI.pyx -o mpi4py_MPI.c
	mv src/mpi4py_MPI.c     src/MPI.c
	mv src/mpi4py_MPI.h     src/mpi4py/include/mpi4py
	mv src/mpi4py_MPI_api.h src/mpi4py/include/mpi4py
