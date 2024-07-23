#!/bin/sh
set -eu
test -f meson.build
test -d src/mpi4py
rm -rf build install
options="--python.bytecompile=-1 --python.platlibdir="""
env CC=mpicc \
meson setup build --prefix="$PWD/install" $options
meson compile -C build
meson install -C build
