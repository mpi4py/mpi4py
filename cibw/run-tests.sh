#!/bin/bash
set -euo pipefail

set -x
python --version
python -m mpi4py --version
python -m mpi4py --prefix
python -m mpi4py --module
python -m mpi4py --mpi-vendor
python -m mpi4py --mpi-library
python -m mpi4py --mpi-abi-version
python -m mpi4py --mpi-std-version
python -m mpi4py --mpi-lib-version
