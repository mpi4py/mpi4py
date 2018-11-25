# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

$MS_DOWNLOAD_URL      = "http://download.microsoft.com/download/"
$MSMPI_HASH_URL_V0500 = "3/7/6/3764A48C-5C4E-4E4D-91DA-68CED9032EDE/"
$MSMPI_HASH_URL_V0600 = "6/4/A/64A7852A-A8C3-476D-908C-30501F761DF3/"
$MSMPI_HASH_URL_V0700 = "D/7/B/D7BBA00F-71B7-436B-80BC-4D22F2EE9862/"
$MSMPI_HASH_URL_V0710 = "E/8/A/E8A080AF-040D-43FF-97B4-065D4F220301/"
$MSMPI_HASH_URL_V0800 = "B/2/E/B2EB83FE-98C2-4156-834A-E1711E6884FB/"
$MSMPI_HASH_URL_V0810 = "D/B/B/DBB64BA1-7B51-43DB-8BF1-D1FB45EACF7A/"
$MSMPI_HASH_URL_V0900 = "2/E/C/2EC96D7F-687B-4613-80F6-E10F670A2D97/"
$MSMPI_HASH_URL_V0901 = "4/A/6/4A6AAED8-200C-457C-AB86-37505DE4C90D/"
$MSMPI_HASH_URL_V1000 = "A/E/0/AE002626-9D9D-448D-8197-1EA510E297CE/"

$MSMPI_HASH_URL = $MSMPI_HASH_URL_V1000
$MSMPI_BASE_URL = $MS_DOWNLOAD_URL + $MSMPI_HASH_URL

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path -Parent
. "$ScriptDir\download.ps1"
$DOWNLOADS = "C:\Downloads\MSMPI"

function InstallMicrosoftMPISDK ($baseurl, $filename) {
    Write-Host "Installing Microsoft MPI SDK"
    $url = $baseurl + $filename
    $filepath = Download $url $filename $DOWNLOADS
    Write-Host "Installing" $filename
    $prog = "msiexec.exe"
    $args = "/quiet /qn /i $filepath"
    Write-Host "Executing:" $prog $args
    Start-Process -FilePath $prog -ArgumentList $args -Wait
    Write-Host "Microsoft MPI SDK installation complete"
}

function InstallMicrosoftMPIRuntime ($baseurl, $filename) {
    Write-Host "Installing Microsoft MPI Runtime"
    $url = $baseurl + $filename
    $filepath = Download $url $filename $DOWNLOADS
    Write-Host "Installing" $filename
    $prog = $filepath
    $args = "-unattend"
    Write-Host "Executing:" $prog $args
    Start-Process -FilePath $prog -ArgumentList $args -Wait
    Write-Host "Microsoft MPI Runtime installation complete"
}

function SaveMicrosoftMPIEnvironment ($filepath) {
    Write-Host "Saving Microsoft MPI environment variables to" $filepath
    $envlist = @("MSMPI_BIN", "MSMPI_INC", "MSMPI_LIB32", "MSMPI_LIB64")
    $stream = [IO.StreamWriter] $filepath
    foreach ($variable in $envlist) {
        $value = [Environment]::GetEnvironmentVariable($variable, "Machine")
        if ($value) { $stream.WriteLine("SET $variable=$value") }
        if ($value) { Write-Host "$variable=$value" }
    }
    $stream.Close()
}

function InstallMicrosoftMPI () {
    InstallMicrosoftMPISDK $MSMPI_BASE_URL "msmpisdk.msi"
    InstallMicrosoftMPIRuntime $MSMPI_BASE_URL "MSMpiSetup.exe"
    SaveMicrosoftMPIEnvironment "SetEnvMPI.cmd"
}

function main () {
    InstallMicrosoftMPI
}

main
