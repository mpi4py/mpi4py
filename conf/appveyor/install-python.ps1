# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
# Credits: Olivier Grisel and Kyle Kastner

$PYTHON_BASE_URL = "https://www.python.org/ftp/python/"
$GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
$GET_PIP_PATH = "C:\get-pip.py"

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent
. "$ScriptDir\download.ps1"
$DOWNLOADS = "C:\Downloads\Python"

function InstallPython ($python_version, $architecture, $python_home) {
    Write-Host "Installing Python $python_version ($architecture-bit) to $python_home"
    if (Test-Path $python_home) {
        Write-Host $python_home "already exists, skipping."
        return
    }
    $py_major = $python_version[0]; $py_minor = $python_version[2]
    $installer_exe = ($py_major + $py_minor) -as [int] -ge 35
    if ($installer_exe) {
        $arch_suffix = @{"32"="";"64"="-amd64"}[$architecture]
        $filename = "python-" + $python_version + $arch_suffix + ".exe"
    } else {
        $arch_suffix = @{"32"="";"64"=".amd64"}[$architecture]
        $filename = "python-" + $python_version + $arch_suffix + ".msi"
    }
    $url = $PYTHON_BASE_URL + $python_version + "/" + $filename
    $filepath = Download $url $filename $DOWNLOADS
    Write-Host "Installing" $filename "to" $python_home
    if ($installer_exe) {
        $prog = "$filepath"
        $args = "/quiet TargetDir=$python_home"
    } else {
        $prog = "msiexec.exe"
        $args = "/quiet /qn /i $filepath TARGETDIR=$python_home"
    }
    Write-Host $prog $args
    Start-Process -FilePath $prog -ArgumentList $args -Wait
    Write-Host "Python $python_version ($architecture-bit) installation complete"
}

function InstallPip ($python_home) {
    $python_path = Join-Path $python_home "python.exe"
    $pip_path = Join-Path $python_home "Scripts\pip.exe"
    if (Test-Path $pip_path) {
        Write-Host "Upgrading pip"
        $args = "-m pip.__main__ install --upgrade pip"
        Write-Host "Executing:" $python_path $args
        Start-Process -FilePath $python_path -ArgumentList $args -Wait
        Write-Host "pip upgrade complete"
    } else {
        Write-Host "Installing pip"
        $webclient = New-Object System.Net.WebClient
        $webclient.DownloadFile($GET_PIP_URL, $GET_PIP_PATH)
        Write-Host "Executing:" $python_path $GET_PIP_PATH
        Start-Process -FilePath $python_path -ArgumentList "$GET_PIP_PATH" -Wait
        Write-Host "pip installation complete"
    }
}

function InstallPipPackage ($python_home, $package) {
    $pip_path = Join-Path $python_home "Scripts\pip.exe"
    Write-Host "Installing/Upgrading $package"
    $args = "install --upgrade $package"
    Write-Host "Executing:" $pip_path $args
    Start-Process -FilePath $pip_path -ArgumentList $args -Wait
    Write-Host "$package install/upgrade complete"
}

function main () {
    InstallPython $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON
    InstallPip $env:PYTHON
    InstallPipPackage $env:PYTHON setuptools
    InstallPipPackage $env:PYTHON wheel
}

main
