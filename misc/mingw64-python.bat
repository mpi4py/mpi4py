@echo off
setlocal ENABLEEXTENSIONS

rem MinGW-w64
rem http://sourceforge.net/projects/mingw-w64/
set MinGW=%ProgramFiles%\mingw-builds\x64-4.8.1-posix-seh-rev5\mingw64
set PATH=%MinGW%\bin;%PATH%
set GENDEF=gendef.exe
set DLLTOOL=dlltool.exe

rem Python 2.7
rem http://www.python.org/download/releases/2.7/
set PYVER=27
set PYDIR=C:\Python%PYVER%
set LIBDIR=%PYDIR%\libs
set DLLDIR=%WinDir%\System32
set LIBNAME=python%PYVER%
set DLLNAME=python%PYVER%

%GENDEF% - %DLLDIR%\%DLLNAME%.dll > %TEMP%\%LIBNAME%.def
%DLLTOOL% --dllname %DLLNAME%.dll --def %TEMP%\%LIBNAME%.def --output-lib %TEMP%\lib%LIBNAME%.a
move /Y %TEMP%\%LIBNAME%.def  %LIBDIR%
move /Y %TEMP%\lib%LIBNAME%.a %LIBDIR%
