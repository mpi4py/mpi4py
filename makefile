.PHONY: default \
	src cython \
	config build test install \
	docs sphinx epydoc \
	sdist \
	clean distclean srcclean docsclean fullclean uninstall

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

docs: sphinx epydoc

clean:
	${PYTHON} setup.py clean --all

distclean:
	-${RM} -r build  _configtest.* *.py[co]
	-${RM} -r MANIFEST dist mpi4py.egg-info
	-${RM} `find . -name '*~'`
	-${RM} `find . -name '*.py[co]'`

srcclean:
	${RM} src/mpi4py_MPI.c
	${RM} src/include/mpi4py/mpi4py_MPI.h
	${RM} src/include/mpi4py/mpi4py_MPI_api.h

docsclean:
	-${RM} -r docs/html

fullclean: distclean srcclean docsclean

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

SPHINXBUILD = sphinx-build
SPHINXOPTS  =
sphinx:
	mkdir -p build/doctrees docs/html/man
	${SPHINXBUILD} -d build/doctrees ${SPHINXOPTS} \
	docs/source docs/html/man

EPYDOCBUILD = ${PYTHON} ./conf/epydocify.py
EPYDOCOPTS  =
epydoc: clean build
	mkdir -p docs/html
	PYTHONPATH=`ls -d build/lib.*`:$$PYTHONPATH \
	${EPYDOCBUILD} ${EPYDOCOPTS} -o docs/html/api 


sdist: src docs
	${PYTHON} setup.py sdist ${SDISTOPT}
