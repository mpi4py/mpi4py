#!/bin/bash
set -e
case "$(uname)" in
Linux) set -x;
  sudo apt install -y mpich libmpich-dev
  cd "/usr/lib/$(arch)-linux-gnu"
  sudo ln -s libmpi{ch,}.so.12
  ;;
Darwin) set -x;
  brew install mpich
  ;;
esac
