#!/bin/bash
set -euo pipefail

merge() {
    echo merge: "$1" ...
    local directory=$(dirname "$1")
    while IFS= read -r line
    do
        if [[ "$line" =~ ^include\ +\"(.*)\"$ ]]
        then
            local include="${BASH_REMATCH[1]}"
            local filename="$directory/$include"
            echo "#include: $include" >> $2
	    merge "$filename" "$2"
        else
            echo "$line" >> "$2"
        fi
    done < $1
}

source=src/mpi4py/MPI.pyx
output=$source
git restore $source || true
cp $source $source.in
echo write: $output
echo "#cython: linetrace=True" > $output
merge $source.in $output
echo wrote: $output

cat <<EOF > .coveragerc
[run]
parallel = True
branch = True
source = mpi4py
plugins = conf.cycoverage
[paths]
source =
  src/mpi4py
  */mpi4py
EOF
