#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""mpi4py: Python bindings for MPI."""

# ruff: noqa: C408
# ruff: noqa: D103
# ruff: noqa: PTH100
# ruff: noqa: PTH118
# ruff: noqa: PTH120
# ruff: noqa: PTH207

import glob
import os
import sys

topdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(topdir, "conf"))

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

python_version_min = (3, 10)
python_version_max = (3, 15)
python_version = sys.version_info[:2]
py_limited_api = python_version_min


def get_metadata():
    import metadata as md

    req_py = ">={}.{}".format(*python_version_min)
    assert req_py == md.get_requires_python()  # noqa: S101
    version = md.get_version()
    readme = md.get_readme()
    return {
        "version": version,
        "long_description": readme["text"],
        "long_description_content_type": readme["content-type"],
    }


def get_build_mpiabi():
    abi = os.environ.get("MPI4PY_BUILD_MPIABI", "").lower()
    return abi in {"true", "yes", "on", "y", "1"}


def get_build_pysabi():
    abi = os.environ.get("MPI4PY_BUILD_PYSABI", "").lower()
    if sys.implementation.name != "cpython":
        return None
    if abi:
        if abi in {"false", "no", "off", "n", "0"}:
            return None
        if abi in {"true", "yes", "on", "y", "1"} | {"abi3"}:
            return py_limited_api
        abi = abi.removesuffix("-abi3")
        abi = abi.removeprefix("cp")
        if "." in abi:
            x, y = abi.split(".")
        else:
            x, y = abi[0], abi[1:]
        return (int(x), int(y))
    if python_version > python_version_max:
        return python_version_max
    return None


# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------


def sources():
    # mpi4py.MPI
    MPI = dict(
        source="src/mpi4py/MPI.pyx",
        depends=[
            "src/mpi4py/*.pyx",
            "src/mpi4py/*.pxd",
            "src/mpi4py/MPI.src/*.pyx",
            "src/mpi4py/MPI.src/*.pxi",
        ],
    )
    #
    return [MPI]


def extensions():
    import mpidistutils

    # MPI extension module
    MPI = dict(
        name="mpi4py.MPI",
        sources=["src/mpi4py/MPI.c"],
        depends=(
            glob.glob("src/*.h")
            + glob.glob("src/lib-mpi/*.h")
            + glob.glob("src/lib-mpi/config/*.h")
            + glob.glob("src/lib-mpi/compat/*.h")
        ),
        include_dirs=["src"],
        define_macros=[],
        configure=mpidistutils.configure_mpi,
    )
    if get_build_mpiabi():
        MPI["define_macros"] += [
            ("PYMPIABI", 1),
        ]
    return [MPI]


def executables():
    import mpidistutils

    # MPI-enabled Python interpreter
    pyexe = dict(
        name="python-mpi",
        optional=True,
        package="mpi4py",
        dest_dir="bin",
        sources=["src/python.c"],
        configure=mpidistutils.configure_pyexe,
    )
    #
    return [pyexe]


# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------

package_info = dict(
    packages=[
        "mpi4py",
        "mpi4py.futures",
        "mpi4py.util",
    ],
    package_data={
        "mpi4py": [
            "*.pxd",
            "MPI*.h",
            "include/mpi4py/*.h",
            "include/mpi4py/*.i",
            "include/mpi4py/*.pxi",
            "py.typed",
            "*.pyi",
            "*/*.pyi",
        ],
    },
    package_dir={"": "src"},
)


def run_setup():
    """Call setuptools.setup(*args, **kwargs)."""
    from mpidistutils import (
        Executable as Exe,
        Extension as Ext,
        build_src,
        setup,
    )

    #
    build_src.sources = sources()
    #
    metadata = get_metadata()
    builder_args = dict(
        ext_modules=[Ext(**ext) for ext in extensions()],
        executables=[Exe(**exe) for exe in executables()],
    )
    #
    sabi = get_build_pysabi()
    if sabi:
        api_ver = "0x{:02X}{:02X}0000".format(*sabi)
        defines = [("Py_LIMITED_API", api_ver)]
        for ext in builder_args["ext_modules"]:
            ext.define_macros.extend(defines)
            ext.py_limited_api = True
        api_tag = "cp{}{}".format(*sabi)
        options = {"bdist_wheel": {"py_limited_api": api_tag}}
        builder_args["options"] = options
    #
    setup_args = dict(
        i
        for d in (
            metadata,
            package_info,
            builder_args,
        )
        for i in d.items()
    )
    #
    setup(**setup_args)


# --------------------------------------------------------------------


def main():
    run_setup()


if __name__ == "__main__":
    if python_version < python_version_min:
        raise SystemExit(
            "error: requires Python version "
            + ".".join(map(str, python_version_min))
        )
    main()


# --------------------------------------------------------------------
