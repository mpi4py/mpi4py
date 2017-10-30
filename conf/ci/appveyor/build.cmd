:: Author:  Lisandro Dalcin
:: Contact: dalcinl@gmail.com
:: Credits: https://packaging.python.org
@ECHO OFF

IF "%DISTUTILS_USE_SDK%" == "1" (
    "C:\Program Files\Microsoft SDKs\Windows\v7.1\Setup\WindowsSdkVer.exe" -q -version:v7.1
    CALL "C:\Program Files\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.cmd" /x64 /release
    SET MSSdk=1
    ECHO Using Windows SDK 7.1 build environment
) ELSE (
    ECHO Using default MSVC build environment
)

ECHO Executing: %*
CALL %* || EXIT 1
