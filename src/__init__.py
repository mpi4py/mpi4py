# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""
This is the **MPI for Python** package.

What is *MPI*?
==============

The *Message Passing Interface*, is a standardized and portable
message-passing system designed to function on a wide variety of
parallel computers. The standard defines the syntax and semantics of
library routines and allows users to write portable programs in the
main scientific programming languages (Fortran, C, or C++). Since
its release, the MPI specification has become the leading standard
for message-passing libraries for parallel computers.

What is *MPI for Python*?
=========================

*MPI for Python* provides MPI bindings for the Python programming
language, allowing any Python program to exploit multiple processors.
This package is constructed on top of the MPI-1/2 specifications and
provides an object oriented interface which closely follows MPI-2 C++
bindings.
"""

__version__   = '1.3'
__author__    = 'Lisandro Dalcin'
__credits__   = 'MPI Forum, MPICH Team, Open MPI Team.'

# --------------------------------------------------------------------

__all__ = ['MPI', 'MPE']

# --------------------------------------------------------------------

def get_include():
    """
    Return the directory in the package that contains header files.

    Extension modules that need to compile against mpi4py should use
    this function to locate the appropriate include directory. Using
    Python distutils (or perhaps NumPy distutils)::

      import mpi4py
      Extension('extension_name', ...
                include_dirs=[..., mpi4py.get_include()])

    """
    from os.path import dirname, join
    return join(dirname(__file__), 'include')

# --------------------------------------------------------------------

def get_config():
    """
    Return a dictionary with information about MPI.
    """
    from os.path import dirname, join
    try:
        from configparser import ConfigParser
    except ImportError:
        from ConfigParser import ConfigParser
    parser = ConfigParser()
    parser.read(join(dirname(__file__), 'mpi.cfg'))
    return dict(parser.items('mpi'))

# --------------------------------------------------------------------

def profile(name='MPE', **kargs):
    """
    Support for the MPI profiling interface.

    Parameters
    ----------
    name : str, optional
       Name of the profiler to load.
    path : list of str, optional
       Additional paths to search for the profiler.
    logfile : str, optional
       Filename prefix for dumping profiler output.
    """
    import sys, os, imp
    try:
        from mpi4py.dl import dlopen, RTLD_NOW, RTLD_GLOBAL
        from mpi4py.dl import dlerror
    except ImportError:
        from ctypes import CDLL as dlopen, RTLD_GLOBAL
        try:
            from DLFCN import RTLD_NOW
        except ImportError:
            RTLD_NOW = 2
        dlerror = None
    #
    def lookup_pymod(name, path):
        for pth in path:
            for suffix, _, kind in imp.get_suffixes():
                if kind == imp.C_EXTENSION:
                    filename = os.path.join(pth, name + suffix)
                    if os.path.isfile(filename):
                        return filename
        return None
    #
    def lookup_dylib(name, path):
        format = []
        for suffix, _, kind in imp.get_suffixes():
            if kind == imp.C_EXTENSION:
                format.append(('', suffix))
        if sys.platform.startswith('win'):
            format.append(('', '.dll'))
        elif sys.platform == 'darwin':
            format.append(('lib', '.dylib'))
        elif os.name == 'posix':
            format.append(('lib', '.so'))
        format.append(('', ''))
        for pth in path:
            for (lib, so) in format:
                filename = os.path.join(pth, lib + name + so)
                if os.path.isfile(filename):
                    return filename
        return None
    #
    logfile = kargs.pop('logfile', None)
    if logfile:
        if name in ('mpe', 'MPE'):
            if 'MPE_LOGFILE_PREFIX' not in os.environ:
                os.environ['MPE_LOGFILE_PREFIX'] = logfile
        if name in ('vt', 'vt-mpi', 'vt-hyb'):
            if 'VT_FILE_PREFIX' not in os.environ:
                os.environ['VT_FILE_PREFIX'] = logfile
    path = kargs.pop('path', None)
    if path is None:
        path = []
    elif isinstance(path, str):
        path = [path]
    else:
        path = list(path)
    #
    if name in ('MPE',):
        path.append(os.path.dirname(__file__))
        filename = lookup_pymod(name, path)
    else:
        prefix = os.path.dirname(__file__)
        path.append(os.path.join(prefix, 'lib-pmpi'))
        filename = lookup_dylib(name, path)
    if filename is None:
        raise ValueError("profiler '%s' not found" % name)
    else:
        filename = os.path.abspath(filename)
    #
    handle = dlopen(filename, RTLD_NOW|RTLD_GLOBAL)
    if handle:
        profile._registry.append((name, (handle, filename)))
    else:
        from warnings import warn
        if dlerror:
            message = dlerror()
        else:
            message = "error loading '%s'" % filename
        warn(message)

profile._registry = []

# --------------------------------------------------------------------

from mpi4py import rc
rc.profile = profile

# --------------------------------------------------------------------
