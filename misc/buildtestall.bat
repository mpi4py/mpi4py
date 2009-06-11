@echo off
setlocal ENABLEEXTENSIONS

set PATH=C:\MinGW\bin;%PATH%

set TEST_PY=26,30,31
set TEST_MPI=deinompi,mpich2_win,msmpi
set TEST_CC=msvc,mingw32

for %%A in (%TEST_PY%)  do (
for %%B in (%TEST_MPI%) do (
for %%C in (%TEST_CC%)  do (
echo --------------------------------------------------------------------------
call :Main %%A %%B %%C
echo --------------------------------------------------------------------------
)))
goto :eof



:Main
set PYVERSION=%1
set MPICONF=%2
set COMPILER=%3
echo Py: %PYVERSION% - MPI: %MPICONF% - CC: %COMPILER%


set PYTHONDIR=C:\Python%PYVERSION%
set PYTHON="%PYTHONDIR%\python.exe"
set MPIDIR=
if %MPICONF%==deinompi   set MPIDIR=%ProgramFiles%\DeinoMPI
if %MPICONF%==mpich2_win set MPIDIR=%ProgramFiles%\MPICH2
if %MPICONF%==msmpi      set MPIDIR=%ProgramFiles%\Microsoft HPC Pack 2008 SDK
set MPIEXEC="%MPIDIR%\bin\mpiexec.exe"

%PYTHON% setup.py -q clean --all
%PYTHON% setup.py -q build  --mpi=%MPICONF% --compiler=%COMPILER%
%PYTHON% setup.py -q install --home=%TEMP%
%PYTHON% setup.py -q clean --all
%MPIEXEC% -n 2 %PYTHON% test\runalltest.py -q --path=%TEMP%\lib\python
del /S /Q %TEMP%\lib\python > NUL
rmdir /S /Q %TEMP%\lib\python\mpi4py
goto :eof
