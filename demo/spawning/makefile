.PHONY: default build test clean

default: build test clean

MASTERS = cpi-master-py cpi-master-c cpi-master-cxx cpi-master-f90
WORKERS = cpi-worker-py cpi-worker-c cpi-worker-cxx cpi-worker-f90

build: ${MASTERS} ${WORKERS}

LANGS=py c cxx f90
test: build
	@for i in ${LANGS}; do \
	    for j in ${LANGS}; do \
                 ./cpi-master-$$i ./cpi-worker-$$j; \
	    done; \
	done 

clean:
	${RM} -r ${MASTERS} ${WORKERS}


MPICC=mpicc
MPICXX=mpicxx
MPIF90=mpif90

# Python
cpi-master-py: cpi-master.py
	echo '#!' `which python` > $@
	cat $< >> $@
	chmod +x $@
cpi-worker-py: cpi-worker.py
	echo '#!' `which python` > $@
	cat $< >> $@
	chmod +x $@

# C
cpi-master-c: cpi-master.c
	${MPICC} $< -o $@
cpi-worker-c: cpi-worker.c
	${MPICC} $< -o $@

# C++
cpi-master-cxx: cpi-master.cxx
	${MPICXX} $< -o $@
cpi-worker-cxx: cpi-worker.cxx
	${MPICXX} $< -o $@

# Fortran 90
cpi-master-f90: cpi-master.f90
	${MPIF90} $< -o $@
cpi-worker-f90: cpi-worker.f90
	${MPIF90} $< -o $@
