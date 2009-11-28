PYTHON=python

MPIEXEC=mpiexec
NP_FLAG= -n
NP_ARG= 5
MPIEXEC_NP=${MPIEXEC} ${NP_FLAG} ${NP_ARG}

.PHONY: test
test:
	${MPIEXEC_NP} ${PYTHON} seq.py
