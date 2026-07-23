#!/bin/sh
set -eu
cd "$(dirname "$0")"/..
shellcheck -x "$@" -- .*/*.sh .*/step-*
shellcheck -x "$@" -- */*.sh */*/*.sh
