#!/bin/bash
set -euo pipefail

wheelhouse=${1:-wheelhouse}

tempdir=$(mktemp -d)
trap 'rm -rf $tempdir' EXIT
for wheel in "$wheelhouse"/*.whl; do
    wheeldir="$tempdir"/$(basename "$wheel").dir
    unzip -qq "$wheel" -d "$wheeldir"
    distinfo=$(basename "$wheeldir"/mpi4py*.dist-info)
    mkdir -p "$wheeldir/${distinfo%%-*}.libs"
    mkdir -p "$wheeldir/mpi4py/.dylibs"
done

libs=""
rpath=""
runpath=""
needed=""

if [ "$(uname)" == Linux ]; then
    mods=("$tempdir"/mpi4py*linux*.dir/mpi4py/MPI.*.so)
    libs=$(find "$tempdir"/mpi4py*linux*.dir/mpi4py*.libs \
                -type f -exec basename {} \; | sort | uniq)
    rpath=$(patchelf --print-rpath --force-rpath "${mods[@]}" | sort | uniq)
    runpath=$(patchelf --print-rpath "${mods[@]}" | sort | uniq)
    needed=$(patchelf --print-needed "${mods[@]}" | sort | uniq)
fi

if [ "$(uname)" == Darwin ]; then
    mods=("$tempdir"/mpi4py*macos*.dir/mpi4py/MPI.*.so)
    libs=$(
        find "$tempdir"/mpi4py*macos*.dir/mpi4py/.dylibs \
             -type f -exec basename {} \; | sort | uniq)
    runpath=$(
        otool -l "${mods[@]}" | sed -n '/RPATH/{n;n;p;}' |
            awk '{print $2}' | sort | uniq)
    needed=$(
        otool -L "${mods[@]}" | \
            awk '/ /{print $1}' | sort | uniq)
fi

if [[ "$(uname)" =~ NT ]]; then
    mods=("$tempdir"/mpi4py*win*.dir/mpi4py/MPI*.pyd)
    for m in "${mods[@]}"; do cp "$m" "$m.dll"; done
    mods=("$tempdir"/mpi4py*win*.dir/mpi4py/MPI.*.dll)
    out="$(mktemp -d)"/dlldeps.txt
    for m in "${mods[@]}"; do
        ldd "$m" | \
            grep -v "$(basename "$m")" | \
            awk '/=>/{print $1}' >> "$out";
    done
    sys='/[a-z]/Windows/System32/'
    win='kernel.*\.dll\|ntdll\.dll'
    api='api-ms-win-crt-.*\.dll'
    api+='\|advapi32\.dll\|bcrypt\.dll\|rpcrt4\.dll'
    api+='\|sechost\.dll\|version\.dll\|ws2_32\.dll'
    crt='msvcrt\.dll\|ucrtbase\.dll\|vcruntime.*\.dll'
    cpy='python.*\.dll'
    ppy='libpypy.*\.dll'
    needed=$(\
       (grep -v -i \
             -e "$sys" -e "$win" -e "$api" \
             -e "$crt" -e "$cpy" -e "$ppy" \
             "$out" || true) | sort -f | uniq)
fi

echo "libs:    $(echo "$libs"    | tr '\n' ' ')"
echo "rpath:   $(echo "$rpath"   | tr '\n' ' ')"
echo "runpath: $(echo "$runpath" | tr '\n' ' ')"
echo "needed:  $(echo "$needed"  | tr '\n' ' ')"

test -z "$libs"
test -z "$rpath"
if [ "$(uname)" == Linux ]; then
    libre='lib(c|dl|pthread|mpi)\.so'
    test -z "$runpath"
    test -z "$(grep -vE "$libre" <<< "$needed" || true)"
fi
if [ "$(uname)" == Darwin ]; then
    pthre='(/opt/(homebrew|local)|/usr/local)/lib'
    libre='lib(System|mpi|pmpi)\..*\.dylib'
    test -z "$(grep -vE "$pthre" <<< "$runpath" || true)"
    test -z "$(grep -vE "$libre" <<< "$needed"  || true)"
fi
if [[ "$(uname)" =~ NT ]]; then
    libre='((i|ms)mpi)\.dll'
    test -z "$(grep -vE "$libre" <<< "$needed"  || true)"
fi
