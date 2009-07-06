.PHONY: default \
	src cython \
	config build test install \
	docs rst2html sphinx sphinx-html sphinx-pdf epydoc epydoc-html \
	sdist \
	clean distclean srcclean docsclean fullclean uninstall

PYTHON = python

default: build

config: 
	${PYTHON} setup.py config ${CONFIGOPT}

build: src
	${PYTHON} setup.py build ${BUILDOPT}

test:
	${MPIEXEC} ${VALGRIND} ${PYTHON} test/runalltest.py < /dev/null

clean:
	${PYTHON} setup.py clean --all

distclean:
	-${RM} -r build  _configtest.* *.py[co]
	-${RM} -r MANIFEST dist mpi4py.egg-info
	-${RM} `find . -name '*.py[co]'`
	-${RM} `find . -name '*~'`

fullclean: distclean srcclean docsclean

# ----

install: build
	${PYTHON} setup.py install ${INSTALLOPT} --home=${HOME}

uninstall:
	-${RM} -r ${HOME}/lib/python/mpi4py
	-${RM} -r ${HOME}/lib/python/mpi4py-*-py*.egg-info

# ----

src: src/MPI.c

srcclean:
	${RM} src/mpi4py.MPI.c
	${RM} src/include/mpi4py/mpi4py.MPI.h
	${RM} src/include/mpi4py/mpi4py.MPI_api.h

CY_SRC_PXD = $(wildcard src/include/mpi4py/*.pxd)
CY_SRC_PXI = $(wildcard src/MPI/*.pxi) $(wildcard src/include/mpi4py/*.pxi)
CY_SRC_PYX = $(wildcard src/MPI/*.pyx)
src/MPI.c: src/mpi4py.MPI.c
src/mpi4py.MPI.c: ${CY_SRC_PXD} ${CY_SRC_PXI} ${CY_SRC_PYX}
	${PYTHON} ./conf/cythonize.py

cython:
	${PYTHON} ./conf/cythonize.py

# ----

docs: rst2html sphinx epydoc

docsclean:
	-${RM} docs/*.html docs/*.pdf
	-${RM} -r docs/usrman docs/apiref

RST2HTML = rst2html
RST2HTMLOPTS = --no-compact-lists --cloak-email-addresses
rst2html:
	${RST2HTML} ${RST2HTMLOPTS} ./LICENSE.txt  > docs/LICENSE.html
	${RST2HTML} ${RST2HTMLOPTS} ./HISTORY.txt  > docs/HISTORY.html
	${RST2HTML} ${RST2HTMLOPTS} ./THANKS.txt   > docs/THANKS.html
	${RST2HTML} ${RST2HTMLOPTS} docs/index.rst > docs/index.html

SPHINXBUILD = sphinx-build
SPHINXOPTS  =
sphinx: sphinx-html sphinx-pdf
sphinx-html:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees docs/usrman
	${SPHINXBUILD} -b html -d build/doctrees ${SPHINXOPTS} \
	docs/source docs/usrman
sphinx-pdf:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees build/latex
	${SPHINXBUILD} -b latex -d build/doctrees ${SPHINXOPTS} \
	docs/source build/latex
	${MAKE} -C build/latex all-pdf > /dev/null
	mv build/latex/*.pdf docs/

EPYDOCBUILD = ${PYTHON} ./conf/epydocify.py
EPYDOCOPTS  =
epydoc: epydoc-html
epydoc-html:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p docs/apiref
	${EPYDOCBUILD} ${EPYDOCOPTS} --html -o docs/apiref

# ----

sdist: src docs
	${PYTHON} setup.py sdist ${SDISTOPT}

# ----
