.PHONY: default

default:
	${MAKE} -C compute-pi
	${MAKE} -C nxtval
	${MAKE} -C mandelbrot
	${MAKE} -C spawning

	${MAKE} -C wrap-c
	${MAKE} -C wrap-f2py
	${MAKE} -C wrap-swig
	${MAKE} -C wrap-boost
	${MAKE} -C wrap-cython

	${MAKE} -C cython
	${MAKE} -C embedding

	${MAKE} -C mpi-ref-v1
	${MAKE} -C init-fini
	${MAKE} -C threads
