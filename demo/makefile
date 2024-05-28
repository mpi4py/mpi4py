.PHONY: default wrap

default:
	$(MAKE) -C compute-pi
	$(MAKE) -C mandelbrot
	$(MAKE) -C nxtval
	$(MAKE) -C reductions
	$(MAKE) -C sequential
	$(MAKE) -C spawning
	$(MAKE) -C profiling

	$(MAKE) -C cython
	$(MAKE) -C embedding
	$(MAKE) -C libmpi-cffi

	$(MAKE) -C mpi-ref-v1
	$(MAKE) -C init-fini
	$(MAKE) -C threads

	$(MAKE) -C futures

	$(MAKE) wrap

wrap:
	$(MAKE) -C wrap-c
	$(MAKE) -C wrap-cffi
	$(MAKE) -C wrap-ctypes
	$(MAKE) -C wrap-cython
	$(MAKE) -C wrap-swig
	$(MAKE) -C wrap-pybind11
	$(MAKE) -C wrap-f2py
	$(MAKE) -C wrap-ctypes-f90
	$(MAKE) -C wrap-ctypes-f08
