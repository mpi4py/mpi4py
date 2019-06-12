@echo off
setlocal ENABLEEXTENSIONS

set TEST_PY=27,35,35,37,38
set TEST_CC=msvc,mingw32
set TEST_MPI=msmpi

for %%A in (%TEST_PY%)  do (
for %%B in (%TEST_CC%)  do (
for %%C in (%TEST_MPI%) do (
echo --------------------------------------------------------------------------------
call :Main %%A %%B %%C
echo --------------------------------------------------------------------------------
)))
goto :eof

:Main
set PYVERSION=%1
set COMPILER=%2
set MPICONF=%3

set PYTHONDIR=C:\Python%PYVERSION%
set PYTHON="%PYTHONDIR%\python.exe"

set MINGWDIR=C:\MinGW
set GCC=%MINGWDIR%\bin\gcc.exe

set MPIDIR==%ProgramFiles%\MPI
if %MPICONF%==msmpi set MPIDIR=%ProgramFiles%\Microsoft MPI
set MPIEXEC="%MPIDIR%\bin\mpiexec.exe"

echo Py: %PYVERSION% - CC: %COMPILER% - MPI: %MPICONF%
if "%PYVERSION%-%COMPILER%"=="25-msvc" goto :eof
if not exist %PYTHON%  goto :eof
if not exist %MPIEXEC% goto :eof
if not exist %GCC% if %COMPILER%==mingw32 goto :eof
if %COMPILER%==mingw32 set PATH=%MINGWDIR%\bin;%PATH%

set INSTALLDIR=%TEMP%\mpi4py-buildtest
set PYPATHDIR=%INSTALLDIR%\lib\python
%PYTHON% setup.py -q clean --all
%PYTHON% setup.py -q build --mpi=%MPICONF% --compiler=%COMPILER%
%PYTHON% setup.py -q install --home=%INSTALLDIR%
%PYTHON% setup.py -q clean --all

set PATH_ORIG=%PATH%
set PATH=%MPIDIR%\bin;%PATH%
%MPIEXEC% -n 2 %PYTHON% test\runtests.py -q -f --path=%PYPATHDIR%
set PATH=%PATH_ORIG%

rmdir /S /Q %INSTALLDIR% > NUL
goto :eof
