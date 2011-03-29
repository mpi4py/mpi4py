@echo off
setlocal ENABLEEXTENSIONS

set TEST_PY=25,26,27,30,31,32
set TEST_MPI=mpich2,openmpi,deinompi,msmpi
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
set MPIDIR==%ProgramFiles%\MPI
if %MPICONF%==mpich2   set MPIDIR=%ProgramFiles%\MPICH2
if %MPICONF%==openmpi  set MPIDIR=%ProgramFiles%\OpenMPI_v1.5.3-win32
if %MPICONF%==deinompi set MPIDIR=%ProgramFiles%\DeinoMPI
if %MPICONF%==msmpi    set MPIDIR=%ProgramFiles%\Microsoft HPC Pack 2008 SDK
set MPIEXEC="%MPIDIR%\bin\mpiexec.exe"
if %COMPILER%==mingw32 set PATH=C:\MinGW\bin;%PATH%

echo Py: %PYVERSION% - MPI: %MPICONF% - CC: %COMPILER%
if "%PYVERSION%-%COMPILER%"=="25-msvc" goto :eof
if not exist %PYTHON%  goto :eof
if not exist %MPIEXEC% goto :eof

set INSTALLDIR=%TEMP%\mpi4py-buildtest
set PYPATHDIR=%INSTALLDIR%\lib\python
%PYTHON% setup.py -q clean --all
%PYTHON% setup.py -q build --mpi=%MPICONF% --compiler=%COMPILER% install --home=%INSTALLDIR%
%PYTHON% setup.py -q clean --all

set PATH_ORIG=%PATH%
set PATH=%MPIDIR%\bin;%PATH%
%MPIEXEC% -n 2 %PYTHON% test\runtests.py -q --path=%PYPATHDIR%
set PATH=%PATH_ORIG%

rmdir /S /Q %INSTALLDIR% > NUL
goto :eof