:: Author:  Lisandro Dalcin
:: Contact: dalcinl@gmail.com
:: Credits: Olivier Grisel and Kyle Kastner
@ECHO OFF

SET COMMAND_TO_RUN=%*

SET WIN_SDK_ROOT=C:\Program Files\Microsoft SDKs\Windows
IF "%PYTHON_VERSION:~0,1%" == "2" SET WIN_SDK_VERSION="v7.0"
IF "%PYTHON_VERSION:~0,1%" == "3" SET WIN_SDK_VERSION="v7.1"

IF "%PYTHON_ARCH%"=="64" (
    ECHO Configuring Windows SDK %WIN_SDK_VERSION% for Python %PYTHON_VERSION% on a 64 bit architecture
    SET DISTUTILS_USE_SDK=1
    SET MSSdk=1
    "%WIN_SDK_ROOT%\%WIN_SDK_VERSION%\Setup\WindowsSdkVer.exe" -q -version:%WIN_SDK_VERSION%
    "%WIN_SDK_ROOT%\%WIN_SDK_VERSION%\Bin\SetEnv.cmd" /x64 /release
    ECHO Executing: %COMMAND_TO_RUN%
    call %COMMAND_TO_RUN% || EXIT 1
) ELSE (
    ECHO Using default MSVC build environment for 32 bit architecture
    ECHO Executing: %COMMAND_TO_RUN%
    call %COMMAND_TO_RUN% || EXIT 1
)
