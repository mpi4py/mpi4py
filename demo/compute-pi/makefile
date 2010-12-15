.PHONY: test

MPIEXEC=mpiexec -n 1
PYTHON=python

test:
	echo 100 | ${MPIEXEC} ${PYTHON} cpi-cco.py
	echo 100 | ${MPIEXEC} ${PYTHON} cpi-rma.py
	echo 100 | ${MPIEXEC} ${PYTHON} cpi-dpm.py
