include ../config.mk
.PHONY: default build test clean
default: test

.PHONY: run-pool run-crawl run-hello run-primes
run-pool: run-cpi run-crawl run-hello run-primes
run-cpi:
	$(MPIEXEC) $(NP_FLAG) 1 $(PYTHON) run_cpi.py
run-crawl:
	$(MPIEXEC) $(NP_FLAG) 1 $(PYTHON) run_crawl.py
run-hello:
	$(MPIEXEC) $(NP_FLAG) 1 $(PYTHON) run_hello.py
run-primes:
	$(MPIEXEC) $(NP_FLAG) 1 $(PYTHON) run_primes.py


.PHONY: run-comm run-julia run-mandelbrot
run-comm: run-julia run-mandelbrot
run-julia:
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) run_julia.py
run-mandelbrot:
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) run_mandelbrot.py


.PHONY: run-cmdline
run-cmdline:
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) -m mpi4py.futures run_cpi.py
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) -m mpi4py.futures run_crawl.py
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) -m mpi4py.futures run_hello.py
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) -m mpi4py.futures run_primes.py
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) -m mpi4py.futures run_julia.py
	$(MPIEXEC) $(NP_FLAG) 5 $(PYTHON) -m mpi4py.futures run_mandelbrot.py


.PHONY: run-unittest
run-unittest:
	$(MPIEXEC) $(NP_FLAG) 1 $(PYTHON) test_futures.py $(opt)
	$(MPIEXEC) $(NP_FLAG) 2 $(PYTHON) test_futures.py $(opt)
	$(MPIEXEC) $(NP_FLAG) 1 $(PYTHON) -m mpi4py.futures test_futures.py $(opt)
	$(MPIEXEC) $(NP_FLAG) 2 $(PYTHON) -m mpi4py.futures test_futures.py $(opt)


build:

test: run-pool run-comm run-cmdline

clean:
