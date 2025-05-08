#!/bin/sh
set -eu
test -f CMakeLists.txt
test -d src/mpi4py
rm -rf build install
set -- -DPython_FIND_UNVERSIONED_NAMES=FIRST "$@"
cmake -B build -DCMAKE_INSTALL_PREFIX=install "$@"
cmake --build   build
cmake --install build
