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
