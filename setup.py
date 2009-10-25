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

descr    = __doc__.split('\n')[1:-1]; del descr[1:3]
devstat  = ['Development Status :: 5 - Production/Stable']

classifiers = """
License :: OSI Approved :: BSD License
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
Operating System :: Microsoft :: Windows
Intended Audience :: Developers
Intended Audience :: Science/Research
Programming Language :: C
Programming Language :: Cython
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

keywords = """
scientific computing
parallel computing
message passing
MPI
"""

platforms = """
Linux
Unix
Mac OS X
Windows
"""

metadata = {
    'name'             : name,
    'version'          : version,
    'description'      : descr.pop(0),
    'long_description' : '\n'.join(descr),
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

metadata['classifiers'] += devstat
metadata['provides'] = ['mpi4py', 'mpi4py.MPI', 'mpi4py.rc',]
metadata['requires'] = ['pickle',]


# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

def ext_modules():
    import sys; WIN = sys.platform.startswith('win')
    # MPI extension module
    MPI = dict(
        name='mpi4py.MPI',
        sources=['src/MPI.c'],
        depends=['src/mpi4py.MPI.c'],
        )
    # MPE extension module
    MPE = dict(
        name='mpi4py.MPE',
        sources=['src/MPE.c'],
        depends=['src/mpi4py.MPE.c',
                 'src/MPE/mpe-log.h'],
        libraries=['mpe-log'],
        runtime_library_dirs=["${ORIGIN}"],
        )
    if WIN: del MPE['runtime_library_dirs']
    #
    return [MPI, MPE][:1]

def libraries():
    import sys; WIN = sys.platform.startswith('win')
    #
    mpe_log = dict(
        name='mpe-log', shared=True,
        target_dir='mpi4py',
        export_symbols=['PyMPELog'],
        sources=['src/MPE/mpe-log.c'],
        depends=['src/MPE/mpe-log.h'],
        macros=[('HAVE_MPE', 1)],
        libraries=['mpe'],
        )
    #
    pmpi_lmpe = dict(
        name='pmpi-lmpe', shared=True,
        target_dir='mpi4py',
        sources=['src/MPE/pmpi-lmpe.c'],
        libraries=[mpe_log['name']],
        runtime_library_dirs=["${ORIGIN}"],
        extra_link_args= [
            '-Wl,-whole-archive',
            '-llmpe',
            '-Wl,-no-whole-archive',
            ],
        )
    if WIN: del pmpi_lmpe['runtime_library_dirs']
    if WIN: del pmpi_lmpe['extra_link_args']
    #
    pmpi_tmpe = dict(
        name='pmpi-tmpe', shared=True,
        target_dir='mpi4py',
        sources=['src/MPE/pmpi-tmpe.c'],
        extra_link_args= [
            '-Wl,-whole-archive',
            '-ltmpe',
            '-Wl,-no-whole-archive',
            ],
        )
    if WIN: del pmpi_tmpe['extra_link_args']
    if WIN: pmpi_tmpe = None
    #
    pmpi_ampe = dict(
        name='pmpi-ampe', shared=True,
        target_dir='mpi4py',
        sources=['src/MPE/pmpi-ampe.c'],
        libraries=['X11'],
        runtime_library_dirs=["${ORIGIN}"],
        extra_link_args= [
            '-Wl,-whole-archive',
            '-lampe', '-lmpe',
            '-Wl,-no-whole-archive',
            ],
        )
    if WIN: pmpi_ampe = None
    pmpi_ampe = None # XXX disabled !
    #
    libs =[
        mpe_log,
        pmpi_lmpe,
        pmpi_tmpe,
        pmpi_ampe, 
        ]
    libs = [(lib['name'], lib) for lib in libs if lib]
    return libs[:0]

def executables():
    import sys
    from distutils import sysconfig
    from distutils.util import split_quoted
    libraries = []
    library_dirs = []
    compile_args = []
    link_args = []
    py_version = sysconfig.get_python_version()
    cfgDict = sysconfig.get_config_vars()
    if not sys.platform.startswith('win'):
        if '-pthread' in cfgDict.get('CC', ''):
            compile_args.append('-pthread')
        libraries = ['python' + py_version]
        for var in ('LIBDIR', 'LIBPL'):
            library_dirs += split_quoted(cfgDict.get(var, ''))
        if '-pthread' in cfgDict.get('LINKCC', ''):
            link_args.append('-pthread')
        for var in ('LDFLAGS',
                    'LIBS', 'MODLIBS', 'SYSLIBS',
                    'LDLAST'):
            link_args += split_quoted(cfgDict.get(var, ''))
    # MPI-enabled Python interpreter
    pyexe = dict(name='python%s-mpi' % py_version,
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
ShLibrary = lambda library:    library
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
          libraries    = [ShLibrary(lib) for lib in libraries()  ],
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
