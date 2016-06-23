@echo off
python -m cython --cleanup 3 -w src %* mpi4py.MPI.pyx
move src\mpi4py.MPI*.h src\mpi4py\include\mpi4py