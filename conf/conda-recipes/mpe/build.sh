#!/bin/bash

test -f ./configure || ./autogen.sh

./configure \
--prefix=$PREFIX \
--enable-PIC \
CFLAGS="-pthread $CFLAGS" \
LDFLAGS="-pthread $LDFLAGS" \
--disable-f77 \
--disable-graphics

make
make install

rm -rf $PREFIX/sbin
rm -rf $PREFIX/share
rm -f  $PREFIX/bin/bt2line
rm -f  $PREFIX/bin/check_callstack
rm -f  $PREFIX/lib/mpe_prof.o
