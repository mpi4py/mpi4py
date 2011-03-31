#!/bin/sh
python -m cython --cleanup 3 -w src -Iinclude $@ mpi4py.MPE.pyx && \
python -m cython --cleanup 3 -w src -Iinclude $@ mpi4py.MPI.pyx && \
mv src/mpi4py.MPI*.h src/include/mpi4py
