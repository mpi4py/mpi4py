#!/bin/sh
# shellcheck disable=SC2086
set -eu

ENV=${ENV:-env}
PYTHON=${PYTHON:-python${py:-}}
MPIEXEC=${MPIEXEC:-mpiexec}

badenv=''
check='MPI4PY_CHECK_MPIEXEC'
warn='PYTHONWARNINGS=always'
pycmd='from mpi4py import MPI'

set -x

if command -v mpichversion > /dev/null; then
    badenv='OMPI_COMM_WORLD_SIZE=1'
fi
if command -v impi_info > /dev/null; then
    badenv='OMPI_COMM_WORLD_SIZE=1'
fi
if command -v ompi_info > /dev/null; then
    badenv='PMI_SIZE=1 HYDI_CONTROL_FD=dummy'
fi

if command -v $MPIEXEC > /dev/null; then
    $ENV $badenv PYTHONWARNINGS=error $MPIEXEC -n 1 $PYTHON -c "$pycmd"
    $ENV $badenv PYTHONWARNINGS=error $MPIEXEC -n 2 $PYTHON -c "$pycmd"
fi


$ENV $check=yes $warn $PYTHON -c "$pycmd;print()" 2>&1 | grep -q ""
$ENV $check=OFF $warn $PYTHON -c "$pycmd;print()" 2>&1 | grep -q ""
$ENV $check=foo $warn $PYTHON -c "$pycmd;print()" 2>&1 | grep -q "$check"

$ENV $badenv          $warn $PYTHON -c "$pycmd;print()" 2>&1 | grep -q "${badenv% *}"
$ENV $badenv $check=1 $warn $PYTHON -c "$pycmd;print()" 2>&1 | grep -q "${badenv% *}"
$ENV $badenv $check=0 $warn $PYTHON -c "$pycmd;print()" 2>&1 | grep -q ""
$ENV $badenv $check=  $warn $PYTHON -c "$pycmd;print()" 2>&1 | grep -q ""
