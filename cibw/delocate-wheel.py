#!/usr/bin/env python
import os
import sys

import delocate.cmd.delocate_wheel as mod
from delocate.delocating import delocate_wheel, filter_system_libs

libmpi = []
for name in ("mpi", "pmpi", "open-pal", "open-rte"):
    for version in (1, 12, 20, 40):
        libmpi.append(f"lib{name}.{version}.dylib")
libmpi = set(libmpi)


def filter_libs(filename):
    if not filter_system_libs(filename):
        return False
    if os.path.basename(filename) in libmpi:
        return False
    return True


def delocate_wheel_patched(*args, **kwargs):
    kwargs["copy_filt_func"] = filter_libs
    return delocate_wheel(*args, **kwargs)


mod.delocate_wheel = delocate_wheel_patched

dyldname = "DYLD_FALLBACK_LIBRARY_PATH"
dyldpath = os.environ.get(dyldname, "").split(":")
dyldpath.append("/usr/local/lib")
dyldpath.append("/opt/homebrew/lib")
dyldpath.append("/opt/local/lib")
os.environ[dyldname] = ":".join(dyldpath)

if __name__ == "__main__":
    sys.exit(mod.main())
