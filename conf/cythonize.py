#!/usr/bin/env python
"""Run Cython with custom options."""

import os
import pathlib
import sys

from Cython.Compiler.Main import main as cython_main


def cythonize(args=None):
    """Run `cython --3str --cleanup 3 <args>...`."""
    if args is None:
        argv = sys.argv[:]
    else:
        arg0 = str(pathlib.Path(__file__).resolve())
        argv = [arg0, *args]

    if "--cleanup" not in argv:
        argv[1:1] = ["--cleanup", "3"]
    if "--3str" not in argv:
        argv[1:1] = ["--3str"]

    cwd = pathlib.Path.cwd()
    sys_argv = sys.argv[:]
    try:
        sys.argv[:] = argv
        cython_main(command_line=1)
    except SystemExit as exc:
        return exc.code
    else:
        return 0
    finally:
        os.chdir(cwd)
        sys.argv[:] = sys_argv


def main():
    """Entry-point to run Cython with custom options."""
    args = sys.argv[1:]
    if not args:
        topdir = pathlib.Path(__file__).resolve().parent.parent
        source = pathlib.Path() / "src" / "mpi4py" / "MPI.pyx"
        target = pathlib.Path() / "src" / "mpi4py" / "MPI.c"
        args += ["--working", str(topdir)]
        args += [str(source), "--output-file", str(target)]
    sys.exit(cythonize(args))


if __name__ == "__main__":
    main()
