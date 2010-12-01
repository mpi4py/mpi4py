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
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% test_seq.py
