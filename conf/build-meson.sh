#!/bin/sh
set -eu
test -f meson.build
test -d src/mpi4py
rm -rf build install
set -- --python.bytecompile=-1 --python.platlibdir="" "$@"
meson setup build --prefix="$PWD"/install "$@"
meson compile -C build
meson install -C build
