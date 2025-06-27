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

uv=$(command -v uv)
: "${UV=${uv:-uv-not-found}}"

scriptdir=$(dirname "${BASH_SOURCE[0]}")
"$UV" pip uninstall -q "$mpipackage"
for version in "${!mpiversion}"; do
    echo "::group::$mpipackage=$version"
    "$UV" pip install "$mpipackage==$version.*"
    "$UV" pip list
    "$UV" run bash "$scriptdir"/run-tests-mpi.sh
    echo "::endgroup::"
done
"$UV" pip uninstall -q "$mpipackage"
