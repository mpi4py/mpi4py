MPIEXEC = mpiexec
NP_FLAG = -n
NP = 3

PYTHON = python$(py)

.PHONY: test
test:
	echo 100 | ${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} cpi-cco.py
	echo 100 | ${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} cpi-rma.py
	echo 100 | ${MPIEXEC} ${NP_FLAG} 1     ${PYTHON} cpi-dpm.py ${NP}
