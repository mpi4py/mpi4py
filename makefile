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
test:
	$(VALGRIND) $(PYTHON) $(PWD)/test/runtests.py $(opt)
test-%:
	$(MPIEXEC) -n $* $(VALGRIND) $(PYTHON) $(PWD)/test/runtests.py $(opt)

.PHONY: srcbuild srcclean
srcbuild:
	$(PYTHON) setup.py build_src $(opt)
srcclean:
	$(RM) src/mpi4py/MPI.c
	$(RM) src/mpi4py/MPI.h
	$(RM) src/mpi4py/MPI_api.h

.PHONY: clean distclean fullclean
clean:
	$(PYTHON) setup.py clean --all
distclean: clean
	-$(RM) -r build _configtest* _skbuild
	-$(RM) -r .ruff_cache .mypy_cache
	-$(RM) -r htmlcov .coverage .coverage.*
	-$(RM) -r conf/__pycache__ test/__pycache__
	-$(RM) -r demo/__pycache__ src/mpi4py/__pycache__
fullclean: distclean srcclean
	-find . -name '*~' -exec rm -f {} ';'

# ----

.PHONY: develop develop-uninstall
develop:
	$(PYTHON) setup.py develop --prefix='' --user $(opt)
develop-uninstall:
	$(PYTHON) setup.py develop --prefix='' --user --uninstall $(opt)

# ----

.PHONY: install uninstall
install:
	$(PYTHON) setup.py install --prefix='' --user $(opt)
uninstall:
	-$(RM) -r $(shell $(PYTHON) -m site --user-site)/mpi4py
	-$(RM) -r $(shell $(PYTHON) -m site --user-site)/mpi4py-*-py*.egg-info

# ----
