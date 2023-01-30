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

__version__ = '4.0.0.dev0'
__author__ = 'Lisandro Dalcin'
__credits__ = 'MPI Forum, MPICH Team, Open MPI Team'


__all__ = ['MPI']


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
    errors : {"exception", "default", "abort", "fatal"}
        Error handling policy (default: "exception").

    """

    initialize = True
    threads = True
    thread_level = 'multiple'
    finalize = None
    fast_reduce = True
    recv_mprobe = True
    errors = 'exception'

    def __init__(self, **kwargs):
        self(**kwargs)

    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise TypeError(f"object has no attribute {name!r}")
        super().__setattr__(name, value)

    def __call__(self, **kwargs):
        for key in kwargs:
            if not hasattr(self, key):
                raise TypeError(f"unexpected argument {key!r}")
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f'<{__name__}.rc>'


rc = Rc()
__import__('sys').modules[__name__ + '.rc'] = rc


def get_include():
    """Return the directory in the package that contains header files.

    Extension modules that need to compile against mpi4py should use
    this function to locate the appropriate include directory. Using
    Python distutils (or perhaps NumPy distutils)::

      import mpi4py
      Extension('extension_name', ...
                include_dirs=[..., mpi4py.get_include()])

    """
    # pylint: disable=import-outside-toplevel
    from os.path import join, dirname
    return join(dirname(__file__), 'include')


def get_config():
    """Return a dictionary with information about MPI."""
    # pylint: disable=import-outside-toplevel
    from os.path import join, dirname
    from configparser import ConfigParser
    config = join(dirname(__file__), 'mpi.cfg')
    parser = ConfigParser()
    parser.read(config, encoding='utf-8')
    return dict(parser.items('mpi'))


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
    import sys
    import warnings

    try:
        from _ctypes import dlopen
        from os import RTLD_NOW, RTLD_GLOBAL
    except ImportError as exc:  # pragma: no cover
        warnings.warn(exc.args[0])
        return

    def find_library(name, path):
        pattern = [('', '')]
        if sys.platform == 'darwin':  # pragma: no cover
            pattern.append(('lib', '.dylib'))
        elif os.name == 'posix':  # pragma: no cover
            pattern.append(('lib', '.so'))
        for pth in path:
            for (lib, dso) in pattern:
                filename = os.path.join(pth, lib + name + dso)
                if os.path.isfile(filename):
                    return os.path.abspath(filename)
        return None

    if path is None:
        path = ['']
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
        warnings.warn(exc.args[0])
    else:
        registry = vars(profile).setdefault('registry', [])
        registry.append((name, (handle, filename)))
