#!/bin/bash
set -euo pipefail

: "${MPIEXEC=mpiexec}"
: "${PYTHON=python}"

{ set -x; } 2>/dev/null
"$PYTHON" -m mpi4py --version
"$PYTHON" -m mpi4py --prefix
"$PYTHON" -m mpi4py --module
"$PYTHON" -m mpi4py --mpi-vendor
"$PYTHON" -m mpi4py --mpi-library
"$PYTHON" -m mpi4py --mpi-abi-version
"$PYTHON" -m mpi4py --mpi-std-version
"$PYTHON" -m mpi4py --mpi-lib-version | { head -n 1; } 2>/dev/null
"$MPIEXEC" -n 2 "$PYTHON" -m mpi4py.bench ringtest
"$MPIEXEC" -n 2 "$PYTHON" -m mpi4py.bench helloworld
{ set +x; } 2>/dev/null
