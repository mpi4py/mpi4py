@echo off
setlocal ENABLEEXTENSIONS
if %PROCESSOR_ARCHITECTURE%==x86 (set ARCH=i386) else (set ARCH=amd64)

rem MinGW-w64
rem http://sourceforge.net/projects/mingw-w64/
set MinGW=%ProgramFiles%\mingw-builds\x64-4.8.1-posix-seh-rev5\mingw64
set PATH=%MinGW%\bin;%PATH%
set GENDEF=gendef.exe
set DLLTOOL=dlltool.exe

rem HPC Pack 2012 MS-MPI Service Pack 1
rem http://www.microsoft.com/en-us/download/details.aspx?id=39961
set MPIDIR="%ProgramFiles%\Microsoft HPC Pack 2012"
set LIBDIR=%MPIDIR%\lib\%ARCH%
set DLLDIR=%WinDir%\System32
set LIBNAME=msmpi
set DLLNAME=msmpi

%GENDEF% - %DLLDIR%\%DLLNAME%.dll > %TEMP%\%LIBNAME%.def
%DLLTOOL% --dllname %DLLNAME%.dll --def %TEMP%\%LIBNAME%.def --output-lib %TEMP%\lib%LIBNAME%.a
move /Y %TEMP%\%LIBNAME%.def  %LIBDIR%
move /Y %TEMP%\lib%LIBNAME%.a %LIBDIR%