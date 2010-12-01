MPIEXEC=mpiexec
NP_FLAG=-n
NP=5

PYTHON=python

.PHONY: test
test:
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test_reductions.py -q
	${RM} -r *.py[co] __pycache__
