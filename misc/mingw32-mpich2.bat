rem @echo off
setlocal ENABLEEXTENSIONS

rem MinGW   -> http://www.mingw.org/wiki/Getting_Started
rem MPICH2  -> http://www.mcs.anl.gov/research/projects/mpich2/downloads/index.php?s=downloads

set MPIDIR="%ProgramFiles%\MPICH2"
set MPILIBDIR=%MPIDIR%\lib
set MPIDLLDIR=%WinDir%\System32
set LIBNAME=mpi
set DLLNAME=mpich2

set PEXPORTS=C:\MinGW\bin\pexports.exe
set DLLTOOL=C:\MinGW\bin\dlltool.exe
%PEXPORTS% %MPIDLLDIR%\%DLLNAME%.dll > %TEMP%\%LIBNAME%.def
%DLLTOOL% --dllname %DLLNAME%.dll --def %TEMP%\%LIBNAME%.def --output-lib %TEMP%\lib%LIBNAME%.a

move %TEMP%\%LIBNAME%.def  %MPILIBDIR%
move %TEMP%\lib%LIBNAME%.a %MPILIBDIR%