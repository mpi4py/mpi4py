#!/bin/sh
# shellcheck disable=SC2086
set -eu

PYTHON=${PYTHON:-python${py:-}}
MPIEXEC=${MPIEXEC:-mpiexec}
NP_FLAG=${NP_FLAG:-'-n'}
NP=${NP:-2}

dir=$(dirname "$0")

set -x
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-2.01.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-2.08.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-2.16.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-2.29.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-2.32.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-2.34.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-2.35.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.01.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.02.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.03.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.04.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.05.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.06.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.07.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.08.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.09.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.11.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.12.py
$MPIEXEC $NP_FLAG $NP $PYTHON "$dir"/ex-3.13.py
