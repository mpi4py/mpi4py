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
echo plm_rsh_agent=false >> $openmpi_mca_params
echo btl=tcp,self >> $openmpi_mca_params
echo mpi_yield_when_idle=true >> $openmpi_mca_params
echo rmaps_base_oversubscribe=true >> $openmpi_mca_params
echo btl_base_warn_component_unused=false >> $openmpi_mca_params
echo btl_vader_single_copy_mechanism=none >> $openmpi_mca_params
prte_mca_params=$HOME/.prte/mca-params.conf
mkdir -p $(dirname $prte_mca_params)
echo rmaps_default_mapping_policy=:oversubscribe >> $prte_mca_params
