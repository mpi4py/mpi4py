@echo off
setlocal ENABLEEXTENSIONS

set PATH=C:\MinGW\bin;%PATH%

set TEST_PY=25,26,27,30,31,32
set TEST_MPI=mpich2,deinompi,msmpi
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

set PYTHONDIR=C:\Python%PYVERSION%
set PYTHON="%PYTHONDIR%\python.exe"
set MPIDIR=
if %MPICONF%==deinompi set MPIDIR=%ProgramFiles%\DeinoMPI
if %MPICONF%==mpich2   set MPIDIR=%ProgramFiles%\MPICH2
if %MPICONF%==msmpi    set MPIDIR=%ProgramFiles%\Microsoft HPC Pack 2008 SDK
set MPIEXEC="%MPIDIR%\bin\mpiexec.exe"

echo Py: %PYVERSION% - MPI: %MPICONF% - CC: %COMPILER%
if "%PYVERSION%-%COMPILER%"=="25-msvc" goto :eof
if not exist %PYTHON%  goto :eof
if not exist %MPIEXEC% goto :eof

set INSTALLDIR=%TEMP%\mpi4py-buildtest
%PYTHON% setup.py -q clean --all
%PYTHON% setup.py -q build  --mpi=%MPICONF% --compiler=%COMPILER% install --home=%INSTALLDIR%
%PYTHON% setup.py -q clean --all
%MPIEXEC% -n 2 %PYTHON% test\runtests.py -q --path=%INSTALLDIR%
del   /S /Q %INSTALLDIR%\lib\python > NUL
rmdir /S /Q %INSTALLDIR%\lib\python\mpi4py > NUL
rmdir /S /Q %INSTALLDIR%
goto :eof
