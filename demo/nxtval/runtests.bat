@echo off
setlocal ENABLEEXTENSIONS

set MPI=Microsoft HPC Pack 2008 SDK
set MPI=DeinoMPI
set MPI=MPICH2

set MPIDIR=%ProgramFiles%\%MPI%
set MPIEXEC="%MPIDIR%\bin\mpiexec.exe"
set NP=-n 5

set PYTHON=C:\Python25\python.exe
set PYTHON=C:\Python26\python.exe
set PYTHON=C:\Python27\python.exe
set PYTHON=C:\Python30\python.exe
set PYTHON=C:\Python31\python.exe
set PYTHON=C:\Python32\python.exe
set PYTHON=python

@echo on
%MPIEXEC% %NP% %PYTHON% nxtval-dynproc.py
%MPIEXEC% %NP% %PYTHON% nxtval-onesided.py
%MPIEXEC% %NP% %PYTHON% nxtval-threads.py
 