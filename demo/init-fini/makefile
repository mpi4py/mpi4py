MPIEXEC=mpiexec
NP_FLAG=-n
NP=3

PYTHON=python

.PHONY: test
test:
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test_0.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test_1.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test_2a.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test_2b.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test_3.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test_4.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} test_5.py
