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

require_python = (3, 8)
maxknow_python = (3, 13)
py_limited_api = (3, 10)


def get_metadata():
    import metadata as md

    req_py = ">={}.{}".format(*require_python)
    assert req_py == md.requires_python  # noqa: S101
    author = md.authors[0]
    readme = md.get_readme()
    return {
        # distutils
        "name": md.get_name(),
        "version": md.get_version(),
        "description": md.description,
        "long_description": readme["text"],
        "classifiers": md.classifiers,
        "keywords": md.keywords,
        "license": md.license,
        "author": author["name"],
        "author_email": author["email"],
        # setuptools
        "project_urls": md.urls,
        "python_requires": md.requires_python,
        "long_description_content_type": readme["content-type"],
    }


def get_build_mpiabi():
    abi = os.environ.get("MPI4PY_BUILD_MPIABI", "").lower()
    return abi in {"true", "yes", "on", "y", "1"}


def get_build_pysabi():
    abi = os.environ.get("MPI4PY_BUILD_PYSABI", "").lower()
    if abi and sys.implementation.name == "cpython":
        if abi in {"false", "no", "off", "n", "0"}:
            return None
        if abi in {"true", "yes", "on", "y", "1"} | {"abi3"}:
            return py_limited_api
        if abi.startswith("cp"):
            abi = abi[2:]
        if "." in abi:
            x, y = abi.split(".")
        else:
            x, y = abi[0], abi[1:]
        return (int(x), int(y))
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
    if sys.version_info[:2] > maxknow_python:
        sabi = get_build_pysabi() or maxknow_python
        lapi = "0x{:02x}{:02x}0000".format(*sabi)
        MPI["define_macros"] += [
            ("CYTHON_LIMITED_API", lapi),
        ]
    #
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
    try:
        import setuptools
    except ImportError as exc:
        setuptools = None
        if sys.version_info >= (3, 12):
            sys.exit(exc)
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
    if setuptools:
        builder_args["zip_safe"] = False
    else:
        metadata.pop("project_urls")
        metadata.pop("python_requires")
        metadata.pop("long_description_content_type")
    #
    sabi = get_build_pysabi()
    if sabi and setuptools:
        api_tag = "cp{}{}".format(*sabi)
        options = {"bdist_wheel": {"py_limited_api": api_tag}}
        builder_args["options"] = options
        api_ver = "0x{:02X}{:02X}0000".format(*sabi)
        defines = [("Py_LIMITED_API", api_ver)]
        for ext in builder_args["ext_modules"]:
            ext.define_macros.extend(defines)
            ext.py_limited_api = True
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


def run_skbuild():
    """Call setuptools.setup(*args, **kwargs)."""
    from setuptools import setup

    #
    metadata = get_metadata()
    builder_args = dict(
        cmake_source_dir=".",
    )
    #
    options = {}
    cmake_args = []
    if get_build_mpiabi():
        cmake_args += ["-DMPIABI:BOOL=1"]
    sabi = get_build_pysabi()
    if sabi:
        api_tag = "cp{}{}".format(*sabi)
        options["bdist_wheel"] = {"py_limited_api": api_tag}
        cmake_args += ["-DPYSABI:STRING={}.{}".format(*sabi)]
    if options:
        builder_args["options"] = options
    if cmake_args:
        builder_args["cmake_args"] = cmake_args
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
    try:
        name = __import__("builder").get_build_backend_name()
    except RuntimeError as exc:
        sys.exit(exc)

    if name == "setuptools":
        run_setup()
    if name == "skbuild":
        run_skbuild()


if __name__ == "__main__":
    if sys.version_info < require_python:
        raise SystemExit(
            "error: requires Python version "
            + ".".join(map(str, require_python))
        )
    main()


# --------------------------------------------------------------------
