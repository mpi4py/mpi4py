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


def profile(name='MPE', **kargs):
    """
    MPI profiling interface
    """
    import sys, os, imp
    #
    try:
        from ctypes import CDLL as dlopen, RTLD_GLOBAL
    except ImportError:
        try:
            from dl import open as dlopen,  RTLD_GLOBAL
        except ImportError:
            raise # XXX better message ?
    try:
        from dl import RTLD_NODELETE
    except ImportError:
        try:
            from DLFCN import RTLD_NODELETE
        except ImportError:
            platform = sys.platform[:6]
            if platform == 'linux2':
                RTLD_NODELETE = 0x01000
            elif platform == 'darwin':
                RTLD_NODELETE = 0x80
            elif platform == 'sunos5':
                RTLD_NODELETE = 0x01000
            else:
                RTLD_NODELETE = 0
    try:
        from dl import RTLD_NOW
    except ImportError:
        try:
            from DLFCN import RTLD_NOW
        except ImportError:
            platform = sys.platform[:6]
            if platform in ('linux2', 'darwin',
                            'sunos5', 'cygwin',):
                RTLD_NOW = 2
            else:
                RTLD_NOW = 0
    #
    prefix = os.path.dirname(__file__)
    so = imp.get_suffixes()[0][0]
    if name == 'MPE': # special case
        filename = os.path.join(prefix, name + so)
    else:
        format = [('', so)]
        if sys.platform.startswith('win'):
            format.append(('', '.dll'))
        elif sys.platform == 'darwin':
            format.append(('lib', '.dylib'))
        elif os.name == 'posix':
            format.append(('lib', '.so'))
        for (lib, so) in format:
            basename = lib + name + so
            filename = os.path.join(prefix, 'lib-pmpi', basename)
            if os.path.isfile(filename):
                break
            else:
                filename = None
        if filename is None:
            relpath = os.path.join(os.path.basename(prefix), 'lib-pmpi')
            raise ValueError(
                "profiler '%s' not found in '%s'" % (name, relpath))
    #
    global libpmpi
    handle = dlopen(filename, RTLD_NOW|RTLD_GLOBAL|RTLD_NODELETE)
    libpmpi = (filename, handle)
    #
    if name == 'MPE':
        if 'MPE_LOGFILE_PREFIX' not in os.environ:
            logfile = kargs.pop('logfile', None)
            if logfile:
                os.environ['MPE_LOGFILE_PREFIX'] = logfile
    #
    return filename
