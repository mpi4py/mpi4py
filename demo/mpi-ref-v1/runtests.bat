@echo off
setlocal ENABLEEXTENSIONS

set MPI=Microsoft HPC Pack 2008 SDK
set MPI=DeinoMPI
set MPI=MPICH2
set PATH="%ProgramFiles%\%MPI%\bin";%PATH%

set MPIEXEC=mpiexec
set NP_FLAG=-n
set NP=5

set PYTHON=C:\Python25\python.exe
set PYTHON=C:\Python26\python.exe
set PYTHON=C:\Python27\python.exe
set PYTHON=C:\Python30\python.exe
set PYTHON=C:\Python31\python.exe
set PYTHON=C:\Python32\python.exe
set PYTHON=python

@echo on
set MPIEXEC=
set NP_FLAG=
set NP=
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-2.01.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-2.08.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-2.16.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-2.29.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-2.32.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-2.34.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-2.35.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.01.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.02.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.03.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.04.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.05.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.06.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.07.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.08.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.09.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.11.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.12.py
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% ex-3.13.py
