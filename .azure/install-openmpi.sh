#!/bin/bash
set -e

case "$(uname)" in
Linux) set -x;
  sudo apt install -y openmpi-bin libopenmpi-dev
  ;;
Darwin) set -x;
  brew install openmpi
  ;;
esac

openmpi_mca_params=$HOME/.openmpi/mca-params.conf
mkdir -p "$(dirname "$openmpi_mca_params")"
cat << EOF > "$openmpi_mca_params"
plm_ssh_agent=false
btl=tcp,self
mpi_yield_when_idle=true
rmaps_base_oversubscribe=true
btl_base_warn_component_unused=false
btl_vader_single_copy_mechanism=none
EOF

prte_mca_params=$HOME/.prte/mca-params.conf
mkdir -p "$(dirname "$prte_mca_params")"
cat << EOF > "$prte_mca_params"
rmaps_default_mapping_policy=:oversubscribe
EOF
