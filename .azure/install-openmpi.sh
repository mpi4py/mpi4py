#!/bin/bash
set -e
case `uname` in
Linux) set -x;
  sudo apt install -y openmpi-bin libopenmpi-dev
  ;;
Darwin) set -x;
  brew install openmpi
  ;;
esac

openmpi_mca_params=$HOME/.openmpi/mca-params.conf
mkdir -p $(dirname $openmpi_mca_params)
echo rmaps_base_oversubscribe=yes >> $openmpi_mca_params
