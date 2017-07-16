.PHONY: default build test clean

MPIEXEC=mpiexec -n 1

default: build test clean

MASTERS = cpi-master-py.exe cpi-master-c.exe cpi-master-cxx.exe cpi-master-f90.exe
WORKERS = cpi-worker-py.exe cpi-worker-c.exe cpi-worker-cxx.exe cpi-worker-f90.exe

build: ${MASTERS} ${WORKERS}

LANGS=py c cxx f90
test: build
	@for i in ${LANGS}; do \
	    for j in ${LANGS}; do \
                 ${MPIEXEC} ./cpi-master-$$i.exe ./cpi-worker-$$j.exe; \
	    done; \
	done 

clean:
	${RM} -r ${MASTERS} ${WORKERS}


MPICC=mpicc
MPICXX=mpicxx
MPIF90=mpif90
ifneq (${MPI_FORTRAN_MOD_DIR},)
FFLAGS += -I${MPI_FORTRAN_MOD_DIR}
endif

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
	${MPICC} $< -o $@
cpi-worker-c.exe: cpi-worker.c
	${MPICC} $< -o $@

# C++
cpi-master-cxx.exe: cpi-master.cxx
	${MPICXX} $< -o $@
cpi-worker-cxx.exe: cpi-worker.cxx
	${MPICXX} $< -o $@

# Fortran 90
cpi-master-f90.exe: cpi-master.f90
	${MPIF90} ${FFLAGS} $< -o $@
cpi-worker-f90.exe: cpi-worker.f90
	${MPIF90} ${FFLAGS} $< -o $@
