@echo off
python -m cython --cleanup 3 -w src -I include %* mpi4py.MPE.pyx
python -m cython --cleanup 3 -w src -I include %* mpi4py.MPI.pyx
move src\mpi4py.MPI*.h src\include\mpi4py