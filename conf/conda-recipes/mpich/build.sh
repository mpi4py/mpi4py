#!/bin/bash
./configure \
  --disable-fortran \
  --disable-dependency-tracking \
  --prefix=$PREFIX
make -j $CPU_COUNT
make install
