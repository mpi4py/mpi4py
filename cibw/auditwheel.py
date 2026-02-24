#!/usr/bin/env python
import os
import sys

from auditwheel.main import main

if "repair" in sys.argv:
    arch = os.uname().machine
    x, y = (2, 5) if arch == "x86_64" else (2, 17)
    plat = f"manylinux_{x}_{y}_{arch}"
    args = ["--plat", plat, "--only-plat"]
    for name in ("mpi", "mpi_abi"):
        args += ["--exclude", f"lib{name}.so.*"]
    sys.argv.extend(args)

sys.exit(main())
