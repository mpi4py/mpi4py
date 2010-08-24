#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

"""
MPI for Python
==============

This package provides MPI support for Python scripting in parallel
environments. It is constructed on top of the MPI-1/MPI-2
specification, but provides an object oriented interface which closely
follows the MPI-2 C++ bindings.

This module supports point-to-point (send, receive) and collective
(broadcast, scatter, gather, reduction) communications of any
*picklable* Python object.

For objects exporting single-segment buffer interface (strings, NumPy
arrays, etc.), blocking/nonbloking/persistent point-to-point,
collective and one-sided (put, get, accumulate) communications are
fully supported, as well as parallel I/O (blocking and nonbloking,
collective and noncollective read and write operations using explicit
file offsets, individual file pointers and shared file
pointers).

There is also full support for group and communicator (inter, intra,
Cartesian and graph topologies) creation and management, as well as
creating user-defined datatypes. Additionally, there is almost
complete support for dynamic process creation and management (spawn,
name publishing).
"""

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

def name():
    return 'mpi4py'

def version():
    import os, re
    data = open(os.path.join('src', '__init__.py')).read()
    m = re.search(r"__version__\s*=\s*'(.*)'", data)
    return m.groups()[0]

name    = name()
version = version()

url      = 'http://%(name)s.googlecode.com/' % vars()
download = url + 'files/%(name)s-%(version)s.tar.gz' % vars()

description = __doc__.split('\n')[1:-1]; del description[1:3]

classifiers = """
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Operating System :: POSIX :: SunOS/Solaris
Operating System :: Unix
Programming Language :: C
Programming Language :: Cython
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Distributed Computing
"""

keywords = """
scientific computing
parallel computing
message passing
MPI
"""

platforms = """
Mac OS X
Linux
Solaris
Unix
Windows
"""

metadata = {
    'name'             : name,
    'version'          : version,
    'description'      : description.pop(0),
    'long_description' : '\n'.join(description),
    'url'              : url,
    'download_url'     : download,
    'classifiers'      : [c for c in classifiers.split('\n') if c],
    'keywords'         : [k for k in keywords.split('\n')    if k],
    'platforms'        : [p for p in platforms.split('\n')   if p],
    'license'          : 'BSD',
    'author'           : 'Lisandro Dalcin',
    'author_email'     : 'dalcinl@gmail.com',
    'maintainer'       : 'Lisandro Dalcin',
    'maintainer_email' : 'dalcinl@gmail.com',
    }

metadata['requires'] = ['pickle',]
metadata['provides'] = ['mpi4py',
                        'mpi4py.dl',
                        'mpi4py.rc',
                        'mpi4py.MPI',
                        'mpi4py.MPE',
                        ]

# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

def ext_modules():
    import sys, os
    modules = []
    # MPI extension module
    MPI = dict(
        name='mpi4py.MPI',
        sources=['src/MPI.c'],
        depends=['src/mpi4py.MPI.c'],
        )
    modules.append(MPI)
    # MPE extension module
    MPE = dict(
        name='mpi4py.MPE',
        optional=True,
        sources=['src/MPE.c'],
        depends=['src/mpi4py.MPE.c',
                 'src/MPE/mpe-log.h',
                 'src/MPE/mpe-log.c',
                 ],
        define_macros=[('HAVE_MPE', 1)],
        libraries=['mpe'],
        extra_link_args=[],
        )
    if sys.platform.startswith('linux'):
        MPE['libraries'] = []
        MPE['extra_link_args'] = [
            '-Wl,-whole-archive',
            '-llmpe',
            '-Wl,-no-whole-archive',
            '-lmpe',
            ]
    modules.append(MPE)
    # custom dl extension module
    dl = dict(
        name='mpi4py.dl',
        optional=True,
        sources=['src/dynload.c'],
        depends=['src/dynload.h'],
        define_macros=[('HAVE_DLFCN_H', 1)],
        libraries=['dl'],
        )
    if os.name == 'posix':
        modules.append(dl)
    #
    return modules

def libraries():
    import sys
    # MPE logging
    pmpi_mpe_log = dict(
        name='mpe-log', kind='dylib',
        output_dir='mpi4py/lib-pmpi',
        sources=['src/MPE/pmpi-lmpe.c'],
        extra_link_args=[
            '-Wl,-whole-archive',
            '-llmpe',
            '-Wl,-no-whole-archive',
            '-lmpe',
            ],
        )
    if sys.platform.startswith('win'):
        pmpi_mpe_log['libraries'] = ['mpe']
        pmpi_mpe_log['extra_link_args'] = []
    # MPE tracing
    pmpi_mpe_trace = dict(
        name='mpe-trace', kind='dylib',
        output_dir='mpi4py/lib-pmpi',
        sources=['src/MPE/pmpi-tmpe.c'],
        extra_link_args= [
            '-Wl,-whole-archive',
            '-ltmpe',
            '-Wl,-no-whole-archive',
            '-lmpe',
            ],
        )
    if sys.platform.startswith('win'):
        pmpi_mpe_trace['extra_link_args'] = []
    # MPE animations
    pmpi_mpe_anim = dict(
        name='mpe-anim', kind='dylib',
        output_dir='mpi4py/lib-pmpi',
        sources=['src/MPE/pmpi-ampe.c'],
        extra_link_args=[
            '-Wl,-whole-archive',
            '-lampe',
            '-Wl,-no-whole-archive',
            '-lmpe',
            '-lX11'
            ],
        )
    if sys.platform.startswith('win'):
        pmpi_mpe_anim['extra_link_args'] = []
    #
    return [#pmpi_mpe_log,   # XXX disabled !
            #pmpi_mpe_trace, # XXX disabled !
            #pmpi_mpe_anim,  # XXX disabled !
            ]

def executables():
    import sys
    from distutils import sysconfig
    from distutils.util import split_quoted
    libraries = []
    library_dirs = []
    compile_args = []
    link_args = []
    py_version = sysconfig.get_python_version()
    if not sys.platform.startswith('win'):
        cfgDict = sysconfig.get_config_vars()
        if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
            libraries = ['python' + py_version]
        if sys.platform == 'darwin':
            fwkdir = cfgDict.get('PYTHONFRAMEWORKDIR')
            if (fwkdir and fwkdir != 'no-framework' and
                fwkdir in cfgDict.get('LINKFORSHARED', '')):
                del libraries[:]
        for var in ('LIBDIR', 'LIBPL'):
            library_dirs += split_quoted(cfgDict.get(var, ''))
        for var in ('LDFLAGS',
                    'LIBS', 'MODLIBS', 'SYSLIBS',
                    'LDLAST'):
            link_args += split_quoted(cfgDict.get(var, ''))
    # MPI-enabled Python interpreter
    pyexe = dict(name='python%s-mpi' % py_version,
                 optional=True,
                 sources=['src/python.c'],
                 libraries=libraries,
                 library_dirs=library_dirs,
                 extra_compile_args=compile_args,
                 extra_link_args=link_args)
    return [pyexe]

# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------

from conf.mpidistutils import setup
from conf.mpidistutils import Distribution, Extension, Executable
from conf.mpidistutils import config, build, install, clean
from conf.mpidistutils import build_ext, build_exe
from conf.mpidistutils import install_data, install_exe

ExtModule = lambda extension:  Extension(**extension)
Library   = lambda library:    (library['name'], library)
ExeBinary = lambda executable: Executable(**executable)

def run_setup():
    """
    Call distutils.setup(*targs, **kwargs)
    """
    setup(packages     = ['mpi4py'],
          package_dir  = {'mpi4py' : 'src'},
          package_data = {'mpi4py' : ['include/mpi4py/*.h',
                                      'include/mpi4py/*.pxd',
                                      'include/mpi4py/*.pyx',
                                      'include/mpi4py/*.pxi',
                                      'include/mpi4py/*.i',]},
          ext_modules  = [ExtModule(ext) for ext in ext_modules()],
          libraries    = [Library(lib)   for lib in libraries()  ],
          executables  = [ExeBinary(exe) for exe in executables()],
          **metadata)

def chk_cython(*C_SOURCE):
    import sys, os
    if os.path.exists(os.path.join(*C_SOURCE)):
        return
    warn = lambda msg='': sys.stderr.write(msg+'\n')
    warn("*"*80)
    warn()
    warn(" You need to generate C source files with Cython!!")
    warn(" Download and install Cython <http://www.cython.org>")
    warn(" and next execute in your shell:")
    warn()
    warn("   $ python ./conf/cythonize.py")
    warn()
    warn("*"*80)

if __name__ == '__main__':
    try:
        run_setup()
    except:
        try:
            chk_cython('src', 'mpi4py.MPI.c')
            chk_cython('src', 'mpi4py.MPE.c')
        finally:
            raise

# --------------------------------------------------------------------
