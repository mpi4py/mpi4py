#!/bin/bash
set -e
case `uname` in
Linux) set -x;
  sudo apt install -y mpich libmpich-dev
  ;;
Darwin) set -x;
  brew install mpich
  ;;
esac
