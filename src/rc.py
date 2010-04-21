# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""
Runtime configuration parameters.
"""

initialize = True
"""
Automatic MPI initialization at import time

* Any of ``{True  | 1 | "yes" }``: initialize MPI at import time
* Any of ``{False | 0 | "no"  }``: do not initialize MPI at import time
"""


threaded = True
"""
Request for thread support at MPI initialization

* Any of ``{True  | 1 | "yes" }``: initialize MPI with ``MPI_Init_thread()``
* Any of ``{False | 0 | "no"  }``: initialize MPI with ``MPI_Init()``
"""


thread_level = "multiple"
"""
Level of thread support to request at MPI initialization

* ``"single"``     : use ``MPI_THREAD_SINGLE``
* ``"funneled"``   : use ``MPI_THREAD_FUNNELED``
* ``"serialized"`` : use ``MPI_THREAD_SERIALIZED``
* ``"multiple"``   : use ``MPI_THREAD_MULTIPLE``
"""


finalize = True
"""
Automatic MPI finalization at exit time

* Any of ``{True  | 1 | "yes" }``: call ``MPI_Finalize()`` at exit time
* Any of ``{False | 0 | "no"  }``: do not call ``MPI_Finalize()`` at exit time
"""


_pmpi_ = []

def profile(name='MPE', **kargs):
    """
    MPI profiling interface
    """
    import sys, os, imp
    #
    try:
        from mpi4py.dl import dlopen, RTLD_NOW, RTLD_GLOBAL
    except ImportError:
        from ctypes import CDLL as dlopen, RTLD_GLOBAL
        try:
            from DLFCN import RTLD_NOW
        except ImportError:
            RTLD_NOW = 2
    #
    prefix = os.path.dirname(__file__)
    so = imp.get_suffixes()[0][0]
    if name == 'MPE': # special case
        filename = os.path.join(prefix, name + so)
        if 'MPE_LOGFILE_PREFIX' not in os.environ:
            logfile = kargs.pop('logfile', None)
            if logfile:
                os.environ['MPE_LOGFILE_PREFIX'] = logfile
    else:
        format = [('', so)]
        if sys.platform.startswith('win'):
            format.append(('', '.dll'))
        elif sys.platform == 'darwin':
            format.append(('lib', '.dylib'))
        elif os.name == 'posix':
            format.append(('lib', '.so'))
        for (lib, _so) in format:
            basename = lib + name + _so
            filename = os.path.join(prefix, 'lib-pmpi', basename)
            if not os.path.isfile(filename):
                filename = None
            else:
                break
        if filename is None:
            relpath = os.path.join(os.path.basename(prefix), 'lib-pmpi')
            raise ValueError(
                "profiler '%s' not found in '%s'" % (name, relpath))
    #
    global _pmpi_
    handle = dlopen(filename, RTLD_NOW|RTLD_GLOBAL)
    _pmpi_.append( (name, (handle, filename)) )
    #
    return filename
