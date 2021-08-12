#!/bin/sh
python -m cython -3 --cleanup 3 -w src $@ mpi4py/MPI.pyx -o mpi4py.MPI.c && \
mv src/mpi4py.MPI*.h src/mpi4py/include/mpi4py
