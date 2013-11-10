rem @echo off
setlocal ENABLEEXTENSIONS

rem MinGW   -> http://www.mingw.org/wiki/Getting_Started
rem OpenMPI -> http://www.open-mpi.org/software/ompi/v1.6/

set MPIDIR="%ProgramFiles%\OpenMPI_v1.6.1-win32"
set MPILIBDIR=%MPIDIR%\lib
set MPIDLLDIR=%MPIDIR%\bin
set LIBNAME=libmpi
set DLLNAME=libmpi

set PEXPORTS=C:\MinGW\bin\pexports.exe
set DLLTOOL=C:\MinGW\bin\dlltool.exe
%PEXPORTS% %MPIDLLDIR%\%DLLNAME%.dll > %TEMP%\%LIBNAME%.def
%DLLTOOL% --dllname %DLLNAME%.dll --def %TEMP%\%LIBNAME%.def --output-lib %TEMP%\lib%LIBNAME%.a

move %TEMP%\%LIBNAME%.def  %MPILIBDIR%
move %TEMP%\lib%LIBNAME%.a %MPILIBDIR%