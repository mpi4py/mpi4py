.PHONY: default
default: build

PYTHON = python

# ----

.PHONY:	config build test
config:
	${PYTHON} setup.py config ${CONFIGOPT}
build: src
	${PYTHON} setup.py build ${BUILDOPT}
test:
	${MPIEXEC} ${VALGRIND} ${PYTHON} ${PWD}/test/runalltest.py < /dev/null

.PHONY: clean distclean fullclean
clean:
	${PYTHON} setup.py clean --all
distclean:
	-${RM} -r build  _configtest* *.py[co]
	-${RM} -r MANIFEST dist mpi4py.egg-info
	-find conf -name '*.py[co]' -exec rm -f {} ';'
	-find test -name '*.py[co]' -exec rm -f {} ';'
	-find src  -name '*.py[co]' -exec rm -f {} ';'
fullclean: distclean srcclean docsclean
	-find .    -name '*~' -exec rm -f {} ';'

# ----

.PHONY: install uninstall
install: build
	${PYTHON} setup.py install ${INSTALLOPT} --home=${HOME}
uninstall:
	-${RM} -r ${HOME}/lib/python/mpi4py
	-${RM} -r ${HOME}/lib/python/mpi4py-*-py*.egg-info

# ----

.PHONY: src
src: src/mpi4py.MPI.c

CY_SRC_PXD = $(wildcard src/include/mpi4py/*.pxd)
CY_SRC_PXI = $(wildcard src/MPI/*.pxi) $(wildcard src/include/mpi4py/*.pxi)
CY_SRC_PYX = $(wildcard src/MPI/*.pyx)
src/mpi4py.MPI.c: ${CY_SRC_PXD} ${CY_SRC_PXI} ${CY_SRC_PYX}
	${PYTHON} ./conf/cythonize.py

.PHONY: cython
cython:
	${PYTHON} ./conf/cythonize.py

.PHONY:
srcclean:
	${RM} src/mpi4py.MPI.c
	${RM} src/include/mpi4py/mpi4py.MPI.h
	${RM} src/include/mpi4py/mpi4py.MPI_api.h

# ----

.PHONY: docs docs-html docs-pdf
docs: docs-html docs-pdf
docs-html: rst2html sphinx-html epydoc-html
docs-pdf: sphinx-pdf epydoc-pdf

RST2HTML = rst2html
RST2HTMLOPTS = --no-compact-lists --cloak-email-addresses
.PHONY: rst2html
rst2html:
	${RST2HTML} ${RST2HTMLOPTS} ./LICENSE.txt > docs/LICENSE.html
	${RST2HTML} ${RST2HTMLOPTS} ./HISTORY.txt > docs/HISTORY.html
	${RST2HTML} ${RST2HTMLOPTS} ./THANKS.txt  > docs/THANKS.html
	${RST2HTML} ${RST2HTMLOPTS} docs/source/index.rst > docs/index.html

SPHINXBUILD = sphinx-build
SPHINXOPTS  =
.PHONY: sphinx sphinx-html sphinx-pdf
sphinx: sphinx-html sphinx-pdf
sphinx-html:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees docs/usrman
	${SPHINXBUILD} -b html -d build/doctrees ${SPHINXOPTS} \
	docs/source/usrman docs/usrman
sphinx-pdf:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees build/latex
	${SPHINXBUILD} -b latex -d build/doctrees ${SPHINXOPTS} \
	docs/source/usrman build/latex
	${MAKE} -C build/latex all-pdf > /dev/null
	mv build/latex/*.pdf docs/

EPYDOCBUILD = ${PYTHON} ./conf/epydocify.py
EPYDOCOPTS  =
.PHONY: epydoc epydoc-html epydoc-pdf
epydoc: epydoc-html epydoc-pdf
epydoc-html:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p docs/apiref
	${EPYDOCBUILD} ${EPYDOCOPTS} --html -o docs/apiref
epydoc-pdf:

.PHONY:
docsclean:
	-${RM} docs/*.html docs/*.pdf
	-${RM} -r docs/usrman docs/apiref

# ----

.PHONY: sdist
sdist: src docs
	${PYTHON} setup.py sdist ${SDISTOPT}

# ----
