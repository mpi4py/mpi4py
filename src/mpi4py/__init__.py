# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""The **MPI for Python** package.

The *Message Passing Interface* (MPI) is a standardized and portable
message-passing system designed to function on a wide variety of
parallel computers. The MPI standard defines the syntax and semantics
of library routines and allows users to write portable programs in the
main scientific programming languages (Fortran, C, or C++). Since its
release, the MPI specification has become the leading standard for
message-passing libraries for parallel computers.

*MPI for Python* provides MPI bindings for the Python programming
language, allowing any Python program to exploit multiple processors.
This package build on the MPI specification and provides an object
oriented interface which closely follows MPI-2 C++ bindings.

"""

__version__ = "4.1.0"
__author__ = "Lisandro Dalcin"
__credits__ = "MPI Forum, MPICH Team, Open MPI Team"


__all__ = ["MPI"]  # noqa: F822


class Rc:
    """Runtime configuration options.

    Attributes
    ----------
    initialize : bool
        Automatic MPI initialization at import (default: True).
    threads : bool
        Request initialization with thread support (default: True).
    thread_level : {"multiple", "serialized", "funneled", "single"}
        Level of thread support to request (default: "multiple").
    finalize : None or bool
        Automatic MPI finalization at exit (default: None).
    fast_reduce : bool
        Use tree-based reductions for objects (default: True).
    recv_mprobe : bool
        Use matched probes to receive objects (default: True).
    irecv_bufsz : int
        Default buffer size in bytes for ``irecv()`` (default = 32768).
    errors : {"exception", "default", "abort", "fatal"}
        Error handling policy (default: "exception").

    """

    initialize = True
    threads = True
    thread_level = "multiple"
    finalize = None
    fast_reduce = True
    recv_mprobe = True
    irecv_bufsz = 32768
    errors = "exception"

    def __init__(self, **kwargs):
        """Initialize options."""
        self(**kwargs)

    def __setattr__(self, name, value):
        """Set option."""
        if not hasattr(self, name):
            raise TypeError(f"object has no attribute {name!r}")
        super().__setattr__(name, value)

    def __call__(self, **kwargs):
        """Update options."""
        for key in kwargs:
            if not hasattr(self, key):
                raise TypeError(f"unexpected argument {key!r}")
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        """Return repr(self)."""
        return f"<{__spec__.name}.rc>"


rc = Rc()
__import__("sys").modules[__spec__.name + ".rc"] = rc


def get_include():
    """Return the directory in the package that contains header files.

    Extension modules that need to compile against mpi4py should use
    this function to locate the appropriate include directory. Using
    Python distutils (or perhaps NumPy distutils)::

      import mpi4py
      Extension('extension_name', ...
                include_dirs=[..., mpi4py.get_include()])

    """
    prefix = __import__("pathlib").Path(__spec__.origin).parent
    return str(prefix / "include")


def get_config():
    """Return a dictionary with information about MPI.

    .. versionchanged:: 4.0.0
       By default, this function returns an empty dictionary. However,
       downstream packagers and distributors may alter such behavior.
       To that end, MPI information must be provided under an ``mpi``
       section within a UTF-8 encoded INI-style configuration file
       :file:`mpi.cfg` located at the top-level package directory.
       The configuration file is read and parsed using the
       `configparser` module.

    """
    prefix = __import__("pathlib").Path(__spec__.origin).parent
    parser = __import__("configparser").ConfigParser()
    parser.add_section("mpi")
    parser.read(prefix / "mpi.cfg", encoding="utf-8")
    return dict(parser.items("mpi"))


def profile(name, *, path=None):
    """Support for the MPI profiling interface.

    Parameters
    ----------
    name : str
       Name of the profiler library to load.
    path : `sequence` of str, optional
       Additional paths to search for the profiler.

    """
    # pylint: disable=import-outside-toplevel
    import os
    import pathlib
    import sys
    import warnings

    try:
        from _ctypes import dlopen
        from os import RTLD_GLOBAL, RTLD_NOW
    except ImportError as exc:  # pragma: no cover
        warnings.warn(exc.args[0], stacklevel=2)
        return

    def find_library(name, path):
        pattern = [("", "")]
        if sys.platform == "darwin":  # pragma: no cover
            pattern.append(("lib", ".dylib"))
        elif os.name == "posix":  # pragma: no cover
            pattern.append(("lib", ".so"))
        for pth in map(pathlib.Path, path):
            for lib, dso in pattern:
                filename = pth / f"{lib}{name}{dso}"
                if filename.is_file():
                    return str(filename.resolve())
        return None

    if path is None:
        path = [""]
    elif isinstance(path, os.PathLike):
        path = [path]
    elif isinstance(path, str):
        path = path.split(os.pathsep)
    elif isinstance(path, bytes):
        path = path.split(os.fsencode(os.pathsep))

    name = os.fsdecode(name)
    path = list(map(os.fsdecode, path))
    filename = find_library(name, path)
    if filename is None:
        raise ValueError(f"profiler {name!r} not found")

    try:
        handle = dlopen(filename, RTLD_NOW | RTLD_GLOBAL)
    except OSError as exc:
        warnings.warn(exc.args[0], stacklevel=2)
    else:
        registry = vars(profile).setdefault("registry", [])
        registry.append((name, (handle, filename)))
