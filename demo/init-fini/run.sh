#!/bin/sh
set -eu

PYTHON=${PYTHON:-python${py:-}}
MPIEXEC=${MPIEXEC:-mpiexec}
NP_FLAG=${NP_FLAG:-'-n'}
NP=${NP:-2}

dir=$(dirname -- "$0")

set -x
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_1.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_2.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_3.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_4.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_5.py"
