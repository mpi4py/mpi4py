#!/bin/bash
# shellcheck disable=SC2034
set -euo pipefail

mpich=("4.3" "4.2" "4.1" "4.0" "3.4")
openmpi=("5.0" "4.1")
impi=("2021.15" "2021.10" "2021.7")
msmpi=()

mpi="$1"
mpipackage="$mpi"
mpiversion="${mpi}[@]"
test "$mpi" = impi && mpipackage=impi_rt

python=$(command -v python)
: "${PYTHON=${python:-python-not-found}}"

scriptdir=$(dirname "${BASH_SOURCE[0]}")
"$PYTHON" -m pip uninstall -qy "$mpipackage"
for version in "${!mpiversion}"; do
    echo "::group::$mpipackage=$version"
    "$PYTHON" -m pip install "$mpipackage==$version.*"
    "$PYTHON" -m pip list
    "$scriptdir"/run-tests-mpi.sh
    echo "::endgroup::"
done
"$PYTHON" -m pip uninstall -qy "$mpipackage"
