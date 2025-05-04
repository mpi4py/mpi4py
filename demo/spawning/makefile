include ../config.mk
.PHONY: default build test clean
default: build test clean

LANGS = py c cxx f90
MASTERS = $(foreach lang,$(LANGS),cpi-master-$(lang).exe)
WORKERS = $(foreach lang,$(LANGS),cpi-worker-$(lang).exe)

build: $(MASTERS) $(WORKERS)

MPIEXEC = mpiexec -n 1
test: build
	@for i in $(LANGS); do \
	    for j in $(LANGS); do \
                 $(MPIEXEC) ./cpi-master-$$i.exe ./cpi-worker-$$j.exe; \
	    done; \
	done

clean:
	$(RM) -r $(MASTERS) $(WORKERS) __pycache__


# Python
cpi-master-py.exe: cpi-master.py
	echo '#!'`which python` > $@
	cat $< >> $@
	chmod +x $@
cpi-worker-py.exe: cpi-worker.py
	echo '#!'`which python` > $@
	cat $< >> $@
	chmod +x $@

# C
cpi-master-c.exe: cpi-master.c
	$(MPICC) $< -o $@
cpi-worker-c.exe: cpi-worker.c
	$(MPICC) $< -o $@

# C++
cpi-master-cxx.exe: cpi-master.cxx
	$(MPICXX) $< -o $@
cpi-worker-cxx.exe: cpi-worker.cxx
	$(MPICXX) $< -o $@

# Fortran 90
cpi-master-f90.exe: cpi-master.f90
	$(MPIFORT) $< -o $@
cpi-worker-f90.exe: cpi-worker.f90
	$(MPIFORT) $< -o $@
