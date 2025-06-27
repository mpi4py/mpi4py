#!/bin/bash
set -euo pipefail

case "$(uname)" in
    Linux)  toolname=auditwheel;;
    Darwin) toolname=delocate-wheel;;
esac

if [ "$(uname)" == Linux ] || [ "$(uname)" == Darwin ]; then
    here=$(cd "$(dirname -- "$0")" && pwd -P)
    filename=$(command -v "$toolname")
    shebang=$(head -n 1 "$filename")
    sed "1 s|^.*$|$shebang|" "$here/$toolname.py" > "$filename"
fi
