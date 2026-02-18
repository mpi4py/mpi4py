# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Support for MPI ABI."""

import importlib.machinery
import importlib.util
import os
import sys
import warnings

MPIABI = None  # type: str | None
LIBMPI = None  # type: str | list[str] | None
LIBMPI_PATH = None  # type: str| list[str] | None
LIBMPI_MODE = None  # type: int | None

if os.name == "posix":  # pragma: no branch
    _LIBMPIABI = {
        "mpich": ("mpi", 12),
        "openmpi": ("mpi", 40),
        "mpiabi": ("mpi_abi", 0),
    }
else:  # pragma: no cover
    _LIBMPIABI = {
        "impi": ("impi", None),
        "msmpi": ("msmpi", None),
        "mpiabi": ("mpi_abi", None),
    }


def _verbose_info(message, verbosity=1):
    if sys.flags.verbose >= verbosity:
        print(f"# [{__name__}] {message}", file=sys.stderr)


def _site_prefixes():
    prefixes = []
    site = sys.modules.get("site")
    if site is not None:  # pragma: no cover
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


def _dlopen_path(default=None):
    runpath = []

    def add_rpath(*directory):
        path = os.path.join(*directory)
        if sys.platform == "darwin":
            path = path or "@rpath"
        if path not in runpath:
            runpath.append(path)

    def add_rpath_prefix(prefix):
        if os.name == "posix":
            if prefix != "/usr":  # pragma: no branch
                add_rpath(prefix, "lib")
        else:
            add_rpath(prefix, "DLLs")
            add_rpath(prefix, "Library", "bin")

    if default is not None:
        if isinstance(default, (str, bytes, os.PathLike)):
            entries = os.fspath(default).split(os.pathsep)
        else:
            entries = list(map(os.fspath, default)) or [""]
        for entry in entries:
            add_rpath(entry)
        return runpath

    for prefix in _site_prefixes():
        add_rpath_prefix(prefix)

    add_rpath("")

    if os.name == "nt":
        impi_root = os.environ.get("I_MPI_ROOT")
        impi_library_kind = os.environ.get("I_MPI_LIBRARY_KIND") or "release"
        msmpi_bin = os.environ.get("MSMPI_BIN")
        if not msmpi_bin:
            msmpi_root = os.environ.get("MSMPI_ROOT")
            if msmpi_root:
                msmpi_bin = os.path.join(msmpi_root, "bin")
        if impi_root:
            add_rpath(impi_root, "bin", "mpi", impi_library_kind)
            add_rpath(impi_root, "bin", impi_library_kind)
            add_rpath(impi_root, "bin")
        if msmpi_bin:
            add_rpath(msmpi_bin)

    if sys.platform == "darwin":
        add_rpath("/usr/local/lib")
        add_rpath("/opt/homebrew/lib")
        add_rpath("/opt/local/lib")

    return runpath


def _dlopen_mode(default=None):
    if default is not None:
        return default
    if sys.platform == "linux":
        return os.RTLD_LAZY | os.RTLD_LOCAL
    if sys.platform == "darwin":
        return os.RTLD_LAZY | os.RTLD_GLOBAL
    if os.name == "posix":
        return os.RTLD_LAZY | os.RTLD_LOCAL
    return None


def _dlopen_filename(libname, version=None):
    suffix = f".{version}" if version is not None else ""
    if sys.platform == "darwin":
        template = "lib{}{}.dylib"
    elif os.name == "posix":
        template = "lib{}.so{}"
    else:
        template = "{}.dll"
    return template.format(libname, suffix)


def _dlopen_libmpi(libmpi=None):  # pragma: no cover
    # pylint: disable=too-many-statements
    ct = importlib.import_module("ctypes")

    def dlopen(name, mode=None):
        if mode is None:
            mode = ct.DEFAULT_MODE
        _verbose_info(f"trying to dlopen {name!r}")
        lib = ct.CDLL(name, mode)
        _ = lib.MPI_Get_version
        _verbose_info(f"MPI library from {name!r}")
        if name is not None and sys.platform == "linux":
            if hasattr(lib, "I_MPI_Check_image_status"):
                if os.path.basename(name) != name:
                    dlopen_impi_libfabric(os.path.dirname(name), mode)
        if name is not None and os.name == "nt":
            if os.path.basename(name).lower() == "impi.dll":
                if os.path.basename(name) != name:
                    dlopen_impi_libfabric(os.path.dirname(name), mode)
        return lib

    def search_impi_libfabric(rootdir):
        if sys.platform == "linux":
            libdir = "lib"
            suffix = ".so.1"
        else:
            libdir = "bin"
            suffix = ".dll"
        for subdir in (
            ("opt", "mpi", "libfabric", libdir),
            ("libfabric", libdir),
            ("libfabric",),
            (libdir, "libfabric"),
            (libdir,),
        ):
            ofi_libdir = os.path.join(rootdir, *subdir)
            ofi_filename = os.path.join(ofi_libdir, f"libfabric{suffix}")
            if os.path.isfile(ofi_filename):
                return ofi_filename
        return None

    def dlopen_impi_libfabric(libdir, mode):
        ofi_library_internal = os.environ.get(
            "I_MPI_OFI_LIBRARY_INTERNAL", ""
        ).lower() not in ("0", "no", "off", "false", "disable")
        ofi_required = os.environ.get("I_MPI_FABRICS") != "shm"
        if not (ofi_library_internal and ofi_required):
            return None
        rootdir = os.path.dirname(libdir)
        if os.path.basename(rootdir).lower() in ("release", "debug"):
            rootdir = os.path.dirname(rootdir)
        ofi_filename = search_impi_libfabric(rootdir)
        if ofi_filename is None:
            return None
        if "FI_PROVIDER_PATH" not in os.environ:
            ofi_libdir = os.path.dirname(ofi_filename)
            ofi_prov = os.path.join(ofi_libdir, "prov")
            ofi_path = ofi_prov if os.path.isdir(ofi_prov) else ofi_libdir
            os.environ["FI_PROVIDER_PATH"] = ofi_path
        _verbose_info(f"trying to dlopen {ofi_filename!r}")
        lib = ct.CDLL(ofi_filename, mode)
        _ = lib.fi_getinfo
        _verbose_info(f"OFI library from {ofi_filename!r}")
        return lib

    def libmpi_basenames():
        if os.name == "posix":
            yield _dlopen_filename("mpi")
        for libname, version in _LIBMPIABI.values():
            yield _dlopen_filename(libname, version)

    def libmpi_filenames(filename, path):
        if filename is None:
            filenames = list(libmpi_basenames())
        elif isinstance(filename, (str, bytes, os.PathLike)):
            filenames = os.fspath(filename).split(os.pathsep)
        else:
            filenames = list(map(os.fspath, filename))
        for directory in path:
            for location in filenames:
                if os.path.basename(location) == location:
                    location = os.path.join(directory, location)
                location = os.path.expandvars(location)
                location = os.path.expanduser(location)
                yield location

    if os.name == "posix":
        try:
            return dlopen(None)
        except (OSError, AttributeError):
            pass
    path = _dlopen_path(LIBMPI_PATH)
    mode = _dlopen_mode(LIBMPI_MODE)
    errors = ["cannot load MPI library"]
    for filename in libmpi_filenames(libmpi, path):
        try:
            return dlopen(filename, mode)
        except OSError as exc:
            errors.append(str(exc))
        except AttributeError as exc:
            errors.append(str(exc))
    raise RuntimeError("\n".join(errors))


def _get_mpiabi_from_libmpi(libmpi=None):
    lib = _dlopen_libmpi(libmpi)
    abi_get_version = getattr(lib, "MPI_Abi_get_version", None)
    if abi_get_version:  # pragma: no cover
        ct = importlib.import_module("ctypes")
        abi_get_version.restype = ct.c_int
        abi_get_version.argtypes = [ct.POINTER(ct.c_int)] * 2
        abi_major, abi_minor = ct.c_int(0), ct.c_int(0)
        ierr = abi_get_version(ct.byref(abi_major), ct.byref(abi_minor))
        if ierr:  # pragma: no cover
            message = f"MPI_Abi_get_version [ierr={ierr}]"
            raise RuntimeError(message)
        if abi_major.value > 0:
            return "mpiabi"
    if os.name == "posix":  # pragma: no branch
        openmpi = hasattr(lib, "ompi_mpi_comm_self")
        mpiabi = "openmpi" if openmpi else "mpich"
    else:  # pragma: no cover
        msmpi = hasattr(lib, "MSMPI_Get_version")
        mpiabi = "msmpi" if msmpi else "impi"
    return mpiabi


def _get_mpiabi_from_string(string):
    table = {ord(c): "" for c in " -_"}
    mpiabi = string.translate(table).lower()
    if os.name == "posix":  # pragma: no branch
        if mpiabi == "impi":
            mpiabi = "mpich"
    else:  # pragma: no cover
        if mpiabi == "mpich":
            mpiabi = "impi"
    return mpiabi


def _get_libmpi_from_mpiabi(mpiabi):
    mpiabi = _get_mpiabi_from_string(mpiabi)
    libname, version = _LIBMPIABI[mpiabi]
    return _dlopen_filename(libname, version)


def _get_mpiabi():
    mpiabi = getattr(_get_mpiabi, "mpiabi", None)
    if mpiabi is None:
        mpiabi = MPIABI or os.environ.get("MPI4PY_MPIABI")
        libmpi = LIBMPI or os.environ.get("MPI4PY_LIBMPI")
        if mpiabi:
            libmpi = _get_libmpi_from_mpiabi(mpiabi)
        mpiabi = _get_mpiabi_from_libmpi(libmpi)
        _get_mpiabi.mpiabi = mpiabi
    return mpiabi


_registry = {}  # type: dict[str, list[str]]


def _register(module, mpiabi):
    mpiabi = _get_mpiabi_from_string(mpiabi)
    registered = _registry.setdefault(module, [])
    if mpiabi not in registered:
        registered.append(mpiabi)


def _get_mpiabi_suffix(module):
    if module not in _registry:
        return None
    mpiabi = _get_mpiabi()
    if mpiabi not in _registry[module]:
        return None
    return f".{mpiabi}" if mpiabi else ""


class _Finder:
    """MPI ABI-aware extension module finder."""

    # pylint: disable=too-few-public-methods
    @classmethod
    def find_spec(cls, fullname, path, target=None):  # noqa: ARG003
        """Find MPI ABI extension module spec."""
        # pylint: disable=unused-argument
        mpiabi_suffix = _get_mpiabi_suffix(fullname)
        if mpiabi_suffix is None:
            return None
        _verbose_info(f"MPI ABI extension module: {fullname!r}")
        _verbose_info(f"MPI ABI extension suffix: {mpiabi_suffix!r}")
        ext_name = fullname.rpartition(".")[2]
        extension_suffixes = importlib.machinery.EXTENSION_SUFFIXES
        spec_from_file_location = importlib.util.spec_from_file_location
        for directory in path:
            for ext_suffix in extension_suffixes:
                filename = f"{ext_name}{mpiabi_suffix}{ext_suffix}"
                location = os.path.join(directory, filename)
                if os.path.isfile(location):
                    return spec_from_file_location(fullname, location)
        warnings.warn(
            f"unsupported MPI ABI {mpiabi_suffix[1:]!r}",
            category=RuntimeWarning,
            stacklevel=2,
        )
        return None


def _install_finder():
    if _Finder not in sys.meta_path:
        sys.meta_path.append(_Finder)
