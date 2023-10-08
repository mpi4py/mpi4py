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
echo plm=isolated >> $openmpi_mca_params
echo btl=tcp,self >> $openmpi_mca_params
echo rmaps_base_oversubscribe=true >> $openmpi_mca_params
echo btl_base_warn_component_unused=false >> $openmpi_mca_params
echo btl_vader_single_copy_mechanism=none >> $openmpi_mca_params
if [[ `uname` == Darwin ]]; then
    # open-mpi/ompi#7516
    echo gds=hash >> $openmpi_mca_params
    # open-mpi/ompi#5798
    echo btl_vader_backing_directory=/tmp >> $openmpi_mca_params
fi
