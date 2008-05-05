.PHONY: default config src build test install uninstall sdist clean distclean

PYTHON = python
CYTHON = cython

default: build

config: 
	${PYTHON} setup.py config ${CONFIGOPT}

src:
	${MAKE} -C src MPI.c

build:
	${PYTHON} setup.py build ${BUILDOPT}

test:
	${MPIEXEC} ${PYTHON} test/runalltest.py < /dev/null

install: build
	${PYTHON} setup.py install ${INSTALLOPT} --home=${HOME}

uninstall:
	-${RM} -r ${HOME}/lib/python/mpi4py
	-${RM} -r ${HOME}/lib/python/mpi4py-*-py*.egg-info

sdist:
	${PYTHON} setup.py sdist ${SDISTOPT}


clean:
	${PYTHON} setup.py clean --all
	-${RM} _configtest.* *.py[co]
	-${MAKE} -C docs clean

distclean: clean 
	-${RM} -r build  *.py[co]
	-${RM} -r MANIFEST dist mpi4py.egg-info
	-${MAKE} -C docs distclean
	-${RM} `find . -name '*~'`
	-${RM} `find . -name '*.py[co]'`
