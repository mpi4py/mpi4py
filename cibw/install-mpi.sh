#!/bin/bash
set -euo pipefail

MPI_ABI=${1:-mpich}
MACHINE=${PROCESSOR_ARCHITECTURE:-$(uname -m)}
MPIARCH=${2:-$MACHINE}
MPIARCH=${MPIARCH/native/$MACHINE}

MPI_CHANNEL=conda-forge
MPI_PACKAGE=${MPI_ABI}
case "$MPI_ABI" in
    mpich)   MPI_VERSION=4 ;;
    openmpi) MPI_VERSION=5 ;;
    msmpi)   MPI_VERSION=10.1.1 ;;
    impi)    MPI_VERSION=2021.16.0 MPI_PACKAGE=impi-devel ;;
esac
case "$(uname)" in
    Linux|Darwin)
        MPI_ROOT=${MPI_ROOT:-/usr/local}
        sudo() { [ "$(id -u)" -eq 0 ] || set -- command sudo "$@"; "$@"; }
        ;;
    *NT*)
        MPI_ROOT=${MPI_ROOT:-~/mpi}
        sudo() { "$@"; }
        ;;
esac

echo "Install Micromamba"
$SHELL <(curl -sL https://micro.mamba.pm/install.sh) <&-
export PATH=$PATH:~/.local/bin
export MAMBA_ROOT_PREFIX=~/micromamba
micromamba config append channels $MPI_CHANNEL
micromamba config append channels nodefaults
micromamba config set channel_priority strict

echo "Install MPI ($MPI_PACKAGE=$MPI_VERSION) [$MACHINE]"
MPI_ROOT=${MPI_ROOT:-/usr/local}
envroot=~/$MPI_ABI
envdir=$envroot/$MACHINE
micromamba create --yes --always-copy \
           --prefix "$envdir" \
           --relocate-prefix "$MPI_ROOT" \
           "$MPI_PACKAGE"="$MPI_VERSION"
test "$(micromamba list --json --prefix "$envdir" attr)" != "[]" && \
micromamba remove --yes --force --prefix "$envdir" attr
micromamba list --prefix "$envdir"

echo "Fix MPI compiler wrappers"
if [ "$MPI_PACKAGE" == mpich ]; then
    files=("$envdir"/bin/mpi{cc,cxx,fort})
    sed -i.orig -E 's/(CC|CXX|FC)="(.*)-(.*)"/\1="\3"/' "${files[@]}"
    sed -i.orig -E 's/(with_wrapper_dl_type)=(r(un)?path)/\1=none/' "${files[@]}"
    sed -i.orig -E 's/(enable_wrapper_rpath)="(.*)"/\1="no"/' "${files[@]}"
    sed -i.orig "s%-Wl,-rpath,$MPI_ROOT/lib%%g" "${files[@]}"
    sed -i.orig "s%-Wl,-commons,use_dylibs%%g" "${files[@]}"
fi
if [ "$MPI_PACKAGE" == openmpi ]; then
    files=("$envdir"/share/openmpi/mpi{cc,c++,fort}-wrapper-data.txt)
    sed -i.orig -E 's/(compiler)=(.*)-(.*)/\1=\3/' "${files[@]}"
    sed -i.orig "s%-Wl,-rpath,$MPI_ROOT/lib%%g" "${files[@]}"
    sed -i.orig "s%-Wl,-allow-shlib-undefined%%g" "${files[@]}"
    sed -i.orig "s%-Wl,-rpath -Wl,\${libdir}%%g" "${files[@]}"
fi

echo "Copying MPI to $MPI_ROOT"
sudo mkdir -p "$MPI_ROOT"
sudo cp -RP "$envdir"/. "$MPI_ROOT"
echo "Rebuild dynamic linker cache"
sudo "$(command -v ldconfig || echo true)"

echo "Display MPI information"
if [ "$MPI_PACKAGE" == mpich   ]; then mpichversion; fi
if [ "$MPI_PACKAGE" == openmpi ]; then ompi_info;    fi

echo "Display MPI compiler wrappers"
echo mpicc:   "$(mpicc   -show 2>&1)"
echo mpicxx:  "$(mpicxx  -show 2>&1)"
echo mpifort: "$(mpifort -show 2>&1)"

if [ "$(uname)" == Darwin ] && [ "$MPIARCH" != "$MACHINE" ]; then
    echo "Install MPI ($MPI_PACKAGE=$MPI_VERSION) [$MPIARCH]"
    envdir1="$envroot/$MACHINE"
    envdir2="$envroot/$MPIARCH"
    env CONDA_SUBDIR=osx-"${MPIARCH/x86_/}" \
    micromamba create --yes --always-copy \
               --prefix "$envdir2" \
               --relocate-prefix "$MPI_ROOT" \
               "$MPI_PACKAGE"="$MPI_VERSION"
    micromamba list --prefix "$envdir2"
    echo "Creating universal MPI dynamic libraries"
    libs=$(find "$envdir2/lib" -type f -name 'lib*.dylib')
    for lib in $libs; do
        lib=$(basename "$lib")
        sudo lipo -create \
              "$envdir1/lib/$lib" \
              "$envdir2/lib/$lib" \
              -output "$MPI_ROOT/lib/$lib"
        lipo -info "$MPI_ROOT/lib/$lib"
    done
fi
