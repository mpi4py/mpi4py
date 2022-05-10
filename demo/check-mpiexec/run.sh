#/bin/sh
set -eu

ENV=${ENV:-env}
PYTHON=${PYTHON:-python${py:-}}
MPIEXEC=${MPIEXEC:-mpiexec}

badenv=''
check='MPI4PY_CHECK_MPIEXEC'
pycmd='from mpi4py import MPI'

set -x

if command -v mpichversion > /dev/null; then
    badenv='OMPI_COMM_WORLD_SIZE=1'
fi
if command -v ompi_info > /dev/null; then
    badenv='PMI_SIZE=1 HYDI_CONTROL_FD=dummy'
fi

if command -v $MPIEXEC > /dev/null; then
    $ENV $badenv $MPIEXEC -n 1 $PYTHON -Werror -c "$pycmd"
    $ENV $badenv $MPIEXEC -n 2 $PYTHON -Werror -c "$pycmd"
fi


$ENV $check=yes $PYTHON -Walways -c "$pycmd;print()" 2>&1 | grep -q ""
$ENV $check=OFF $PYTHON -Walways -c "$pycmd;print()" 2>&1 | grep -q ""
$ENV $check=foo $PYTHON -Walways -c "$pycmd;print()" 2>&1 | grep -q "$check"

$ENV $badenv          $PYTHON -Walways -c "$pycmd;print()" 2>&1 | grep -q "${badenv% *}"
$ENV $badenv $check=1 $PYTHON -Walways -c "$pycmd;print()" 2>&1 | grep -q "${badenv% *}"
$ENV $badenv $check=0 $PYTHON -Walways -c "$pycmd;print()" 2>&1 | grep -q ""
