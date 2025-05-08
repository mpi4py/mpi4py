#!/bin/sh
set -eu
cd "$(dirname "$0")"/..
shellcheck "$@" -- .*/*.sh .*/step-*
shellcheck "$@" -- */*.sh */*/*.sh
