@echo off
setlocal ENABLEEXTENSIONS

set PATH=C:\MinGW\bin;%PATH%

set TEST_PY=25,26,27,30,31,32
set TEST_MPI=mpich2,openmpi,deinompi,msmpi
set TEST_CC=msvc,mingw32
set TEST_PY=25
set TEST_MPI=openmpi
set TEST_CC=mingw32

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
if %MPICONF%==mpich2   set MPIDIR=%ProgramFiles%\MPICH2
if %MPICONF%==openmpi  set MPIDIR=%ProgramFiles%\OpenMPI_v1.5.1-win32
if %MPICONF%==deinompi set MPIDIR=%ProgramFiles%\DeinoMPI
if %MPICONF%==msmpi    set MPIDIR=%ProgramFiles%\Microsoft HPC Pack 2008 SDK
set MPIEXEC="%MPIDIR%\bin\mpiexec.exe"

echo Py: %PYVERSION% - MPI: %MPICONF% - CC: %COMPILER%
if "%PYVERSION%-%COMPILER%"=="25-msvc" goto :eof
if not exist %PYTHON%  goto :eof
if not exist %MPIEXEC% goto :eof

set INSTALLDIR=%TEMP%\mpi4py-buildtest
set PYPATHDIR=%INSTALLDIR%\lib\python
%PYTHON% setup.py -q clean --all
%PYTHON% setup.py -q build  --mpi=%MPICONF% --compiler=%COMPILER% install --home=%INSTALLDIR%
%PYTHON% setup.py -q clean --all
if %MPICONF%==openmpi copy "%MPIDIR%\bin\lib*.dll" %PYPATHDIR%\mpi4py > NUL
%MPIEXEC% -n 2 %PYTHON% test\runtests.py -q --path=%PYPATHDIR%
del   /S /Q %PYPATHDIR% > NUL
rmdir /S /Q %PYPATHDIR%\mpi4py > NUL
rmdir /S /Q %INSTALLDIR%
goto :eof
