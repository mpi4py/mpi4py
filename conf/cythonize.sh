#!/bin/sh
python -m cython -3 --cleanup 3 -w src $@ mpi4py/MPI.pyx
