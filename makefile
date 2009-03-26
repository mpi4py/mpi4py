.PHONY: default \
	src cython \
	config build test install \
	docs sphinx sphinx-html sphinx-pdf epydoc \
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
	-${RM} -r docs/html docs/*.pdf

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
sphinx: sphinx-html sphinx-pdf
sphinx-html:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees docs/html/man
	${SPHINXBUILD} -b html -d build/doctrees ${SPHINXOPTS} \
	docs/source docs/html/man
sphinx-pdf:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees build/latex
	${SPHINXBUILD} -b latex -d build/doctrees ${SPHINXOPTS} \
	docs/source build/latex
	${MAKE} -C build/latex all-pdf > /dev/null
	mv build/latex/*.pdf docs/

EPYDOCBUILD = ${PYTHON} ./conf/epydocify.py
EPYDOCOPTS  =
epydoc:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p docs/html
	${EPYDOCBUILD} ${EPYDOCOPTS} --html -o docs/html/api 

sdist: src docs
	${PYTHON} setup.py sdist ${SDISTOPT}
