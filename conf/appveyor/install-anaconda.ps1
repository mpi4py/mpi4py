# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

$ANACONDA_BASE_URL = "http://repo.continuum.io/miniconda/"
$ANACONDA_VERSION = "3.19.0"

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent
. "$ScriptDir\download.ps1"
$DOWNLOADS = "C:\Downloads\Anaconda"

function InstallAnaconda ($python_version, $architecture, $anaconda_home) {
    $python_version = $python_version.SubString(0,1)
    Write-Host "Installing Anaconda $ANACONDA_VERSION (Python $python_version, $architecture-bit) to $anaconda_home"
    if (Test-Path $anaconda_home) {
        Write-Host $anaconda_home "already exists, skipping."
        return
    }
    $pver = @{"2"="2";"3"="3"}[$python_version]
    $arch = @{"32"="x86";"64"="x86_64"}[$architecture]
    $filename = "Miniconda" + $pver + "-" + $ANACONDA_VERSION + "-Windows-" + $arch + ".exe"
    $url = $ANACONDA_BASE_URL + $filename
    $filepath = Download $url $filename $DOWNLOADS
    Write-Host "Installing" $filename "to" $anaconda_home
    $prog = $filepath
    $args = "/S /D=$anaconda_home"
    Write-Host "Executing:" $prog $args
    Start-Process -FilePath $prog -ArgumentList $args -Wait
    Write-Host "Updating Anaconda packages"
    $prog = Join-Path $anaconda_home "Scripts\conda.exe"
    $args = "update --yes --quiet --all"
    Write-Host "Executing:" $prog $args
    Start-Process -FilePath $prog -ArgumentList $args -Wait
    Write-Host "Installing additional Anaconda packages"
    $prog = Join-Path $anaconda_home "Scripts\conda.exe"
    $args = "install --yes --quiet anaconda-client conda-build jinja2"
    Write-Host "Executing:" $prog $args
    Start-Process -FilePath $prog -ArgumentList $args -Wait
    Write-Host "Anaconda installation complete"
}

function UpdateAnaconda ($anaconda_home) {
    Write-Host "Updating Anaconda"
    $conda = Join-Path $anaconda_home "Scripts\conda.exe"
    $commands = @(
        "update  --yes --quiet --all",
        "install --yes --quiet anaconda-client conda-build jinja2"
    )
    foreach($args in $commands) {
        Write-Host "Executing:" $conda $args
        Start-Process -FilePath $conda -ArgumentList $args -Wait
    }
}

function main () {
    InstallAnaconda $env:PYTHON_VERSION $env:PYTHON_ARCH $env:ANACONDA
    #UpdateAnaconda $env:ANACONDA
}

main
