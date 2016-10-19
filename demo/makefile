PYTHON=python
.PHONY: default
default:
	${MAKE} PYTHON=${PYTHON} -C compute-pi
	${MAKE} PYTHON=${PYTHON} -C mandelbrot
	${MAKE} PYTHON=${PYTHON} -C nxtval
	${MAKE} PYTHON=${PYTHON} -C reductions
	${MAKE} PYTHON=${PYTHON} -C sequential
	${MAKE} PYTHON=${PYTHON} -C spawning

	${MAKE} PYTHON=${PYTHON} -C wrap-c
	${MAKE} PYTHON=${PYTHON} -C wrap-f2py
	${MAKE} PYTHON=${PYTHON} -C wrap-swig
	${MAKE} PYTHON=${PYTHON} -C wrap-boost
	${MAKE} PYTHON=${PYTHON} -C wrap-cython
	${MAKE} PYTHON=${PYTHON} -C wrap-ctypes
	${MAKE} PYTHON=${PYTHON} -C wrap-cffi

	${MAKE} PYTHON=${PYTHON} -C cython
	${MAKE} PYTHON=${PYTHON} -C embedding
	${MAKE} PYTHON=${PYTHON} -C libmpi-cffi

	${MAKE} PYTHON=${PYTHON} -C mpi-ref-v1
	${MAKE} PYTHON=${PYTHON} -C init-fini
	${MAKE} PYTHON=${PYTHON} -C threads

	${MAKE} PYTHON=${PYTHON} -C futures
