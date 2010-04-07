MPIEXEC=mpiexec
NP_FLAG=-n
NP=5

PYTHON=python

.PHONY: test
test:
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} nxtval-threads.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} nxtval-dynproc.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} nxtval-onesided.py
	${MPIEXEC} ${NP_FLAG} ${NP} ${PYTHON} nxtval-scalable.py
