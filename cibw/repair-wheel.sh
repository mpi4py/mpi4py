#!/bin/bash
set -euo pipefail

usage() { echo "usage: $0 -w {dest_dir} {wheel}" && exit 1; }

test "${1:-}" = "-w" || usage
test "${2:-}" != ""  || usage
test "${3:-}" != ""  || usage

dest_dir=$2
wheel=$3
arch=$(uname -m)

case "$(uname)" in
    Linux)
        case "${arch}" in
            x86_64)  glibc=2_5  ;;
            aarch64) glibc=2_17 ;;
        esac
        auditwheel repair \
            --plat "manylinux_${glibc}_${arch}" \
            --only-plat \
            --exclude "libmpi_abi.so.1" \
            --exclude "libmpi.so.12" \
            --exclude "libmpi.so.40" \
            -w "${dest_dir}" "${wheel}"
        ;;
    Darwin)
        delocate-wheel -v \
            --require-archs "${arch}" \
            --exclude "libmpi_abi.1.dylib" \
            --exclude "libmpi.12.dylib" \
            --exclude "libpmpi.12.dylib" \
            --exclude "libmpi.40.dylib" \
            --exclude "libopen-pal.40.dylib" \
            --exclude "libopen-rte.40.dylib" \
            -w "${dest_dir}" "${wheel}"
        ;;
    *NT*)
        delvewheel repair -v \
            --exclude "mpi_abi.dll" \
            --exclude "impi.dll" \
            --exclude "msmpi.dll" \
            -w "${dest_dir}" "${wheel}"
        ;;
esac
