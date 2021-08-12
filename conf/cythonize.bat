@echo off
python -m cython -3 --cleanup 3 -w src %* mpi4py.MPI.pyx -o mpi4py.MPI.c
move src\mpi4py.MPI*.h src\mpi4py\include\mpi4py
