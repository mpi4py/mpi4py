#!/bin/bash
set -euo pipefail

MPI_ABI=${1:-mpich}
MACHINE=${PROCESSOR_ARCHITECTURE:-$(uname -m)}
MPIARCH=${2:-$MACHINE}
MPIARCH=${MPIARCH/native/$MACHINE}

case "$(uname)" in
    Linux|Darwin)
        MPI_ROOT=${MPI_ROOT:-/usr/local}
        sudo() { [ "$(id -u)" -eq 0 ] || set -- command sudo "$@"; "$@"; }
        ;;
    *NT*)
        MPI_ROOT=${MPI_ROOT:-~/$MPI_ABI}
        sudo() { "$@"; }
        ;;
esac

workdir=$(mktemp -d)
trap 'rm -rf $workdir' EXIT
cd "$workdir"

if [ "$MPI_ABI" == mpiabi ]; then
    echo "Download MPI (mpi-abi-stubs)"
    giturl=https://github.com/mpi-forum/mpi-abi-stubs.git
    rm -rf mpiabi
    git clone --quiet --depth 1 "$giturl" mpiabi
    echo "Install MPI (mpi-abi-stubs) [$MACHINE]"
    options+=(-DCMAKE_INSTALL_PREFIX="$MPI_ROOT")
    options+=(-DCMAKE_INSTALL_LIBDIR="lib")
    cmake -S mpiabi -B mpiabi/build "${options[@]}"
    cmake --build mpiabi/build --config Release
    sudo cmake --install mpiabi/build --config Release
    rm -rf mpiabi
    echo "Rebuild dynamic linker cache"
    sudo "$(command -v ldconfig || echo true)"
    exit 0
fi

echo "Install MPI ($MPI_ABI) [$MACHINE]"
destdir=./$MPI_ABI/$MACHINE
case "$(uname)" in
    Linux|Darwin)
        uv pip install --target "$destdir" "$MPI_ABI"
        rm -r "$destdir"/*.dist-info
        ;;
    *NT*)
        mkdir -p "$destdir"
        case "$MPI_ABI" in
            msmpi)
                nuget install MSMPISDK
                stagedir=$(ls -d MSMPISDK.*/)
                mv "$stagedir"/Lib "$destdir"
                mv "$stagedir"/Include "$destdir"
                rooturl="https://download.microsoft.com/download/"
                hashurl="7/2/7/72731ebb-b63c-4170-ade7-836966263a8f"
                curl -sSLO "$rooturl$hashurl"/MSMpiSetup.exe
                ./MSMpiSetup.exe -unattend
            ;;
            impi)
                nuget install intelmpi.devel.win-x64
                stagedir=$(ls -d intelmpi.redist.*/runtimes/win-x64/native)
                mv "$stagedir"/bin "$destdir"
                mv "$stagedir"/etc "$destdir"
                mv "$stagedir"/libfabric "$destdir"
                stagedir=$(ls -d intelmpi.devel.*/build/native)
                mv "$stagedir"/win-x64/lib "$destdir"
                mv "$stagedir"/include "$destdir"
            ;;
        esac
        ;;
esac

echo "Fix MPI compiler wrappers"
if [ "$MPI_ABI" == mpich ]; then
    files=("$destdir"/bin/mpi{cc,cxx})
    sed -i.orig -E 's/(CC|CXX|FC)="(.*)-(.*)"/\1="\3"/' "${files[@]}"
    sed -i.orig -E 's/(with_wrapper_dl_type)=(r(un)?path)/\1=none/' "${files[@]}"
    sed -i.orig "s%-Wl,-commons,use_dylibs%%g" "${files[@]}"
fi
if [ "$MPI_ABI" == openmpi ]; then
    files=("$destdir"/share/openmpi/mpi{cc,c++}-wrapper-data.txt)
    sed -i.orig -E 's/(compiler)=(.*)-(.*)/\1=\3/' "${files[@]}"
    sed -i.orig "s%\s*-Wl,-rpath -Wl,\${libdir}%%g" "${files[@]}"
    sed -i.orig "s%\s*-Wl,-allow-shlib-undefined%%g" "${files[@]}"
fi

echo "Copying MPI to $MPI_ROOT"
sudo mkdir -p "$MPI_ROOT"
sudo cp -RP "$destdir"/. "$MPI_ROOT"

echo "Rebuild dynamic linker cache"
sudo "$(command -v ldconfig || echo true)"

echo "Display MPI information"
case "$MPI_ABI" in
    mpich)    "$MPI_ROOT"/bin/mpichversion ;;
    openmpi)  "$MPI_ROOT"/bin/ompi_info ;;
    impi)     echo I_MPI_ROOT="$MPI_ROOT" ;;
    msmpi)    echo MSMPI_SDK="$MPI_ROOT" ;;
esac

echo "Display MPI compiler wrappers"
if [ "$(uname)" == Linux ] || [ "$(uname)" == Darwin ] ; then
    echo mpicc:  "$(mpicc   -show 2>&1)"
    echo mpicxx: "$(mpicxx  -show 2>&1)"
else
    echo INCLUDE: "$(find "$MPI_ROOT" -name 'mpi.h')"
    echo LIBRARY: "$(find "$MPI_ROOT" -name '*mpi.lib')"
fi

if [ "$(uname)" == Darwin ] && [ "$MPIARCH" != "$MACHINE" ]; then
    echo "Install MPI ($MPI_ABI) [$MPIARCH]"
    destdir1=./$MPI_ABI/$MACHINE
    destdir2=./$MPI_ABI/$MPIARCH
    case "$MPIARCH" in
        arm64)  pyplat=aarch64-apple-darwin ;;
        x86_64) pyplat=x86_64-apple-darwin ;;
    esac
    uv pip install --target "$destdir2" --python-platform "$pyplat" "$MPI_ABI"
    rm -r "$destdir2"/*.dist-info
    echo "Creating universal MPI dynamic libraries"
    dylibs=$(cd "$destdir1" && find lib -type f -name 'lib*.dylib')
    for dylib in $dylibs; do
        input1=$destdir1/$dylib
        input2=$destdir2/$dylib
        output=$MPI_ROOT/$dylib
        sudo lipo -create "$input1" "$input2" -output "$output"
        sudo lipo -info "$output"
    done
fi
