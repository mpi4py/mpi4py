#!/bin/sh
python -m cython --cleanup 3 -w src $@ mpi4py.MPI.pyx && \
mv src/mpi4py.MPI*.h src/mpi4py/include/mpi4py
