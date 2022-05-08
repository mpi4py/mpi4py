PYTHON = python$(py)
MPIEXEC = mpiexec
NP_FLAG = -n
NP = 2

.PHONY: test
test:
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_1.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_2.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_3.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_4.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_5.py
