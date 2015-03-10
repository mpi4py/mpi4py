#!/bin/bash
./configure \
  --disable-mpi-fortran \
  --disable-dependency-tracking \
  --prefix=$PREFIX
make -j $CPU_COUNT
make install
