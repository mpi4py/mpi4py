.PHONY: default
default: build

PYTHON  = python$(py)
MPIEXEC = mpiexec

# ----

.PHONY: config build test
config:
	${PYTHON} setup.py config $(opt)
build:
	${PYTHON} setup.py build $(opt)
test:
	${VALGRIND} ${PYTHON} ${PWD}/test/runtests.py
test-%:
	${MPIEXEC} -n $* ${VALGRIND} ${PYTHON} ${PWD}/test/runtests.py

.PHONY: srcbuild srcclean
srcbuild:
	${PYTHON} setup.py build_src $(opt)
srcclean:
	${RM} src/mpi4py.MPI.c
	${RM} src/mpi4py/include/mpi4py/mpi4py.MPI.h
	${RM} src/mpi4py/include/mpi4py/mpi4py.MPI_api.h

.PHONY: clean distclean fullclean
clean:
	${PYTHON} setup.py clean --all
distclean: clean
	-${RM} -r build  _configtest* *.py[co]
	-${RM} -r MANIFEST dist
	-${RM} -r conf/__pycache__ test/__pycache__
	-${RM} -r demo/__pycache__ src/mpi4py/__pycache__
	-find conf -name '*.py[co]' -exec rm -f {} ';'
	-find demo -name '*.py[co]' -exec rm -f {} ';'
	-find test -name '*.py[co]' -exec rm -f {} ';'
	-find src  -name '*.py[co]' -exec rm -f {} ';'
fullclean: distclean srcclean docsclean
	-find . -name '*~' -exec rm -f {} ';'

# ----

.PHONY: install uninstall
install: build
	${PYTHON} setup.py install --prefix='' --user $(opt)
uninstall:
	-${RM} -r $(shell ${PYTHON} -m site --user-site)/mpi4py
	-${RM} -r $(shell ${PYTHON} -m site --user-site)/mpi4py-*-py*.egg-info

# ----

.PHONY: docs docs-html docs-pdf docs-misc
docs: docs-html docs-pdf docs-misc
docs-html: rst2html sphinx-html epydoc-html
docs-pdf:  sphinx-pdf epydoc-pdf
docs-misc: sphinx-man sphinx-info

RST2HTML = $(shell command -v rst2html || command -v rst2html.py || false)
RST2HTMLOPTS  = --input-encoding=utf-8
RST2HTMLOPTS += --no-compact-lists
RST2HTMLOPTS += --cloak-email-addresses
.PHONY: rst2html
rst2html:
	${RST2HTML} ${RST2HTMLOPTS} ./LICENSE.rst  > docs/LICENSE.html
	${RST2HTML} ${RST2HTMLOPTS} ./CHANGES.rst  > docs/CHANGES.html
	${RST2HTML} ${RST2HTMLOPTS} docs/index.rst > docs/index.html

SPHINXBUILD = sphinx-build
SPHINXOPTS  =
.PHONY: sphinx sphinx-html sphinx-pdf sphinx-man sphinx-info
sphinx: sphinx-html sphinx-pdf sphinx-man sphinx-info
sphinx-html:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees docs/usrman
	${SPHINXBUILD} -b html -d build/doctrees ${SPHINXOPTS} \
	docs/source/usrman docs/usrman
	${RM} docs/usrman/.buildinfo
sphinx-pdf:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees build/latex
	${SPHINXBUILD} -b latex -d build/doctrees ${SPHINXOPTS} \
	docs/source/usrman build/latex
	${MAKE} -C build/latex all-pdf > /dev/null
	mv build/latex/*.pdf docs/
sphinx-man:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees build/man
	${SPHINXBUILD} -b man -d build/doctrees ${SPHINXOPTS} \
	docs/source/usrman build/man
	mv build/man/*.[137] docs/
sphinx-info:
	${PYTHON} -c 'import mpi4py.MPI'
	mkdir -p build/doctrees build/texinfo
	${SPHINXBUILD} -b texinfo -d build/doctrees ${SPHINXOPTS} \
	docs/source/usrman build/texinfo
	${MAKE} -C build/texinfo info > /dev/null
	mv build/texinfo/*.info docs/

PYTHON2 = python2
EPYDOCBUILD = ${PYTHON2} ./conf/epydocify.py
EPYDOCOPTS  =
.PHONY: epydoc epydoc-html epydoc-pdf
epydoc: epydoc-html epydoc-pdf
epydoc-html:
	mkdir -p docs/apiref
	${PYTHON2} -c 'import epydoc, docutils'
	env CFLAGS=-O0 ${PYTHON2} setup.py -q build --build-lib build/lib.py2 2> /dev/null
	env PYTHONPATH=$$PWD/build/lib.py2 ${EPYDOCBUILD} ${EPYDOCOPTS} --html -o docs/apiref
epydoc-pdf:

.PHONY: docsclean
docsclean:
	-${RM} docs/*.info docs/*.[137]
	-${RM} docs/*.html docs/*.pdf
	-${RM} -r docs/usrman docs/apiref

# ----

.PHONY: sdist
sdist: srcbuild docs
	${PYTHON} setup.py sdist $(opt)

# ----
