#!/bin/bash
set -euo pipefail

dist=${1:-dist}

sudo () {
    [ "$(id -u)" -eq 0 ] || set -- command sudo "$@"
    "$@"
}

# shellcheck disable=SC1091
(source /etc/os-release && echo "::group::$NAME $VERSION")

if grep -qE 'ID=(debian|ubuntu)' /etc/os-release; then
    packages=(
        python3-venv
        pypy3
        libmpich12
        libopenmpi3
    )
    export DEBIAN_FRONTEND=noninteractive
    sudo apt update -y
    sudo apt install -y "${packages[@]}"
    libdir=/usr/lib/$(uname -m)-linux-gnu
    test -L "$libdir"/libmpi.so.12 || \
    sudo ln -sr "$libdir"/libmpi{ch,}.so.12
fi

if grep -qE 'ID=fedora' /etc/os-release; then
    packages=(
        python3.10
        python3.11
        python3.12
        python3.13
        python3.14
        python3.13t
        python3.14t
        pypy3.11
        mpich
        openmpi
    )
    opts=(--setopt=install_weak_deps=False)
    sudo dnf install -y "${opts[@]}" "${packages[@]}"
    set +u
    # shellcheck disable=SC1091
    source /etc/profile.d/modules.sh
    set -u
fi

echo "::endgroup::"

sdir=$(cd "$(dirname -- "$0")" && pwd -P)
"$sdir"/wheel-test-basic.sh "$dist"
