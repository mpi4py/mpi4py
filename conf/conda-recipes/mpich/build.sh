#!/bin/bash
export CC=${CC-cc}
export CXX=${CXX-c++}
./configure \
  --disable-fortran \
  --disable-dependency-tracking \
  --prefix=$PREFIX

sedinplace() { [[ $(uname) == Darwin ]] && sed -i "" $@ || sed -i"" $@; }
sedinplace s%--prefix=$PREFIX%--prefix=\$PREFIX%g src/include/mpichinfo.h
sedinplace s%--prefix=$PREFIX%--prefix=\$PREFIX%g src/pm/hydra/include/hydra_config.h
sedinplace s%-I$(dirname $SRC_DIR)%-I%g           src/pm/hydra/include/hydra_config.h

make -j $CPU_COUNT
make install
