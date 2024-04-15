#!/bin/sh
set -eu
topdir=$(cd $(dirname "$0")/.. && pwd)
python "$topdir/conf/cythonize.py" \
    --working "$topdir" $@ \
    "src/mpi4py/MPI.pyx"
