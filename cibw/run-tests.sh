#!/bin/bash
set -euo pipefail

case "$(uname)" in
    Linux)
        ;;
    Darwin)
        ;;
    *NT*)
        if [ -n "${MSMPI_BIN-}" ]; then
            export PATH="$MSMPI_BIN;$PATH"
        fi
        if [ -n "${I_MPI_ROOT-}" ]; then
            export PATH="$I_MPI_ROOT\\bin;$PATH"
        fi
        ;;
esac

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
