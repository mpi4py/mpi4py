#!/bin/sh
# shellcheck disable=SC2086
set -eu

PYTHON=${PYTHON:-python${py:-}}
MPIEXEC=${MPIEXEC:-mpiexec}
NP_FLAG=${NP_FLAG:-'-n'}
NP=${NP:-2}

dir=$(dirname "$0")

set -x
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" threads=true
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" threads=false
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" thread_level=single
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" thread_level=funneled
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" thread_level=serialized
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" thread_level=multiple
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" fast_reduce=true
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" fast_reduce=false
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" recv_mprobe=true
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" recv_mprobe=false
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" irecv_bufsz=0
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" irecv_bufsz=1
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" irecv_bufsz=1024
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" errors=default
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" errors=exception
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" errors=abort
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_0.py" errors=fatal
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_1.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_2.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_3.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_4.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_5.py"
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir/test_6.py"
