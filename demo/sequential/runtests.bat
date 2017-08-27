@echo off
setlocal ENABLEEXTENSIONS

set MPI=Microsoft MPI
set PATH="%ProgramFiles%\%MPI%\bin";%PATH%

set MPIEXEC=mpiexec
set NP_FLAG=-n
set NP=5

set PYTHON=C:\Python27\python.exe
set PYTHON=C:\Python36\python.exe
set PYTHON=python

@echo on
%MPIEXEC% %NP_FLAG% %NP% %PYTHON% test_seq.py
