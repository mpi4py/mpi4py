.PHONY: default
default:
	${MAKE} -C compute-pi
	${MAKE} -C mandelbrot
	${MAKE} -C nxtval
	${MAKE} -C reductions
	${MAKE} -C sequential
	${MAKE} -C spawning
	${MAKE} -C profiling

	${MAKE} -C wrap-c
	${MAKE} -C wrap-f2py
	${MAKE} -C wrap-swig
	${MAKE} -C wrap-boost
	${MAKE} -C wrap-cython
	${MAKE} -C wrap-ctypes
	${MAKE} -C wrap-cffi

	${MAKE} -C cython
	${MAKE} -C embedding
	${MAKE} -C libmpi-cffi

	${MAKE} -C mpi-ref-v1
	${MAKE} -C init-fini
	${MAKE} -C threads

	${MAKE} -C futures
