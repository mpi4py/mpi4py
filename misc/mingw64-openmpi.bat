@echo off
setlocal ENABLEEXTENSIONS
if %PROCESSOR_ARCHITECTURE%==x86 (set ARCH=win32) else (set ARCH=x64)

rem MinGW-w64
rem http://sourceforge.net/projects/mingw-w64/
set MinGW=%ProgramFiles%\mingw-builds\x64-4.8.1-posix-seh-rev5\mingw64
set PATH=%MinGW%\bin;%PATH%
set GENDEF=gendef.exe
set DLLTOOL=dlltool.exe

rem OpenMPI
rem http://www.open-mpi.org/software/ompi/v1.6/
set MPIDIR="%ProgramFiles%\OpenMPI_v1.6.2-%ARCH%"
set LIBDIR=%MPIDIR%\lib
set DLLDIR=%MPIDIR%\bin
set LIBNAME=libmpi
set DLLNAME=libmpi

%GENDEF% - %DLLDIR%\%DLLNAME%.dll > %TEMP%\%LIBNAME%.def
%DLLTOOL% --dllname %DLLNAME%.dll --def %TEMP%\%LIBNAME%.def --output-lib %TEMP%\lib%LIBNAME%.a
move /Y %TEMP%\%LIBNAME%.def  %LIBDIR%
move /Y %TEMP%\lib%LIBNAME%.a %LIBDIR%
