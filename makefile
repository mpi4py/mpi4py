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
	-${RM} -r build _configtest*
	-${RM} -r MANIFEST dist
	-${RM} -r conf/__pycache__ test/__pycache__
	-${RM} -r demo/__pycache__ src/mpi4py/__pycache__
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
docs-html: rst2html sphinx-html
docs-pdf:  sphinx-pdf
docs-misc: sphinx-man sphinx-info

RST2HTML = $(shell command -v rst2html5.py || command -v rst2html5 || false)
RST2HTMLOPTS = --config=conf/docutils.conf
.PHONY: rst2html
rst2html:
	${RST2HTML} ${RST2HTMLOPTS} LICENSE.rst    docs/LICENSE.html
	${RST2HTML} ${RST2HTMLOPTS} CHANGES.rst    docs/CHANGES.html
	${RST2HTML} ${RST2HTMLOPTS} docs/index.rst docs/index.html

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

.PHONY: docsclean
docsclean:
	-${RM} docs/*.info docs/*.[137]
	-${RM} docs/*.html docs/*.pdf
	-${RM} -r docs/usrman

# ----

.PHONY: sdist
sdist: srcbuild docs
	${PYTHON} setup.py sdist $(opt)

# ----
