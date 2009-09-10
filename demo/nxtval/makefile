PYTHON=python

MPIEXEC=mpiexec
NP_FLAG= -n
NP_ARG= 5
MPIEXEC_NP=${MPIEXEC} ${NP_FLAG} ${NP_ARG}

.PHONY: test
test:
	${MPIEXEC_NP} ${PYTHON} nxtval-threads.py
	${MPIEXEC_NP} ${PYTHON} nxtval-dynproc.py
	${MPIEXEC_NP} ${PYTHON} nxtval-onesided.py
