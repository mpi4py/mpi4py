.PHONY: default
default: build
default: opt=--inplace

PYTHON  = python$(py)
MPIEXEC = mpiexec

# ----

.PHONY: config build test
config:
	$(PYTHON) setup.py config $(opt)
build:
	$(PYTHON) setup.py build $(opt)
check:
	$(PYTHON) -m mpi4py --prefix
	$(PYTHON) -m mpi4py --mpi-library
	$(MPIEXEC) -n 2 $(PYTHON) -m mpi4py.bench ringtest
test:
	$(VALGRIND) $(PYTHON) $(PWD)/test/main.py $(opt)
test-%:
	$(MPIEXEC) -n $* $(VALGRIND) $(PYTHON) $(PWD)/test/main.py $(opt)

.PHONY: srcbuild srcclean
srcbuild:
	$(PYTHON) setup.py build_src $(opt)
srcclean:
	$(RM) src/mpi4py/MPI.c
	$(RM) src/mpi4py/MPI.h
	$(RM) src/mpi4py/MPI_api.h
	$(RM) src/lib-mpi/pympiconf.h

.PHONY: clean distclean fullclean
clean:
	$(PYTHON) setup.py clean --all
distclean: clean srcclean
	$(RM) -r build _configtest*
	$(RM) -r .*_cache .eggs .tox
	$(RM) -r htmlcov .coverage .coverage.*
	$(RM) src/mpi4py/MPI.*.so
	find . -name __pycache__ | xargs $(RM) -r
fullclean: distclean
	find . -name '*~' -exec $(RM) -f {} ';'

# ----

.PHONY: install editable uninstall

install:
	$(PYTHON) -m pip install $(opt) .
editable:
	$(PYTHON) -m pip install --editable $(opt) .
uninstall:
	$(PYTHON) -m pip uninstall $(opt) mpi4py

# ----
