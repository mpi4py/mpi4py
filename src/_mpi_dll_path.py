# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Add MPI to Python DLL search path on Windows."""

# ruff: noqa: PTH100
# ruff: noqa: PTH113
# ruff: noqa: PTH118

import os
import sys


def _verbose_info(message, verbosity=1):
    if sys.flags.verbose >= verbosity:
        print(f"# [{__name__}] {message}", file=sys.stderr)


def _site_prefixes():
    prefixes = []
    site = sys.modules.get("site")
    if site is not None:
        if sys.exec_prefix != sys.base_exec_prefix:
            venv_base = sys.exec_prefix
            prefixes.append(venv_base)
        if site.ENABLE_USER_SITE:
            user_base = os.path.abspath(site.USER_BASE)
            prefixes.append(user_base)
        if sys.base_exec_prefix in site.PREFIXES:
            system_base = sys.base_exec_prefix
            prefixes.append(system_base)
    return prefixes


def _mpi_dll_directories():
    impi_root = os.environ.get("I_MPI_ROOT")
    impi_library_kind = os.environ.get("I_MPI_LIBRARY_KIND") or "release"
    impi_ofi_library_internal = os.environ.get(
        "I_MPI_OFI_LIBRARY_INTERNAL", ""
    ).lower() in ("", "1", "yes", "on", "true", "enable")
    impi_library_path = (
        ("bin", "mpi", impi_library_kind),
        ("bin", impi_library_kind),
        ("bin",),
    )
    impi_ofi_library_path = (
        ("opt", "mpi", "libfabric", "bin"),
        ("libfabric", "bin"),
        ("bin", "libfabric"),
        ("libfabric",),
    )
    msmpi_bin = os.environ.get("MSMPI_BIN")
    if not msmpi_bin:
        msmpi_root = os.environ.get("MSMPI_ROOT")
        if msmpi_root:
            msmpi_bin = os.path.join(msmpi_root, "bin")

    dlldirs = []

    def add_dlldir(*directory, dll=""):
        dlldir = os.path.join(*directory)
        if dlldir not in dlldirs:
            filename = os.path.join(dlldir, f"{dll}.dll")
            if os.path.isfile(filename):
                dlldirs.append(dlldir)
                return True
        return False

    def add_dlldir_impi(*rootdir):
        for subdir in impi_library_path:
            if add_dlldir(*rootdir, *subdir, dll="impi"):
                break
        if impi_ofi_library_internal:
            for subdir in impi_ofi_library_path:
                if add_dlldir(*rootdir, *subdir, dll="libfabric"):
                    break

    def add_dlldir_msmpi(*bindir):
        add_dlldir(*bindir, dll="msmpi")

    for prefix in _site_prefixes():
        add_dlldir_impi(prefix, "Library")
        add_dlldir_msmpi(prefix, "Library", "bin")
    if impi_root:
        add_dlldir_impi(impi_root)
    if msmpi_bin:
        add_dlldir_msmpi(msmpi_bin)

    return dlldirs


_registry = {}


def _add_dll_directory(dlldir):
    os_add_dll_directory = getattr(os, "add_dll_directory", lambda _: None)
    dlldir = os.path.realpath(dlldir)
    if dlldir not in _registry:
        path = os.environ["PATH"].split(os.path.pathsep)
        if dlldir not in set(map(os.path.realpath, path)):
            _verbose_info(f"adding {dlldir!r} to PATH")
            os.environ["PATH"] += os.path.pathsep + dlldir
        _verbose_info(f"adding {dlldir!r} to DLL directories")
        _registry[dlldir] = os_add_dll_directory(dlldir)


def install():
    """Add MPI to Python DLL search path on Windows."""
    for dlldir in _mpi_dll_directories():
        _add_dll_directory(dlldir)
