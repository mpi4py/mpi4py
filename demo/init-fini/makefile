include ../config.mk
.PHONY: default build test clean
default: test

build:

NP = 2
test:
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py threads=true
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py threads=false
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py thread_level=single
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py thread_level=funneled
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py thread_level=serialized
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py thread_level=multiple
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py fast_reduce=true
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py fast_reduce=false
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py recv_mprobe=true
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py recv_mprobe=false
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py errors=default
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py errors=exception
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py errors=abort
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_0.py errors=fatal
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_1.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_2.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_3.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_4.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_5.py
	$(MPIEXEC) $(NP_FLAG) $(NP) $(PYTHON) test_6.py

clean:
