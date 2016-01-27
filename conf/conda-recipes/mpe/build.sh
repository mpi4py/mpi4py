#!/bin/bash

conda_install() { conda install -y -q -p /home/anaconda/env $@; }
command -v libtoolize > /dev/null || \
conda_install --channel asmeurer libtool
test -f ./configure || \
conda_install --channel asmeurer m4 autoconf
test -f ./configure || ./autogen.sh

./configure \
--prefix=$PREFIX \
--enable-PIC \
CFLAGS=-pthread \
LDFLAGS=-pthread \
--disable-f77 \
--disable-graphics

make
make install

rm -rf $PREFIX/sbin
rm -rf $PREFIX/share
rm -f  $PREFIX/bin/bt2line
rm -f  $PREFIX/bin/check_callstack
rm -f  $PREFIX/lib/mpe_prof.o
