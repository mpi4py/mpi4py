#! /usr/bin/env python
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

name     = 'mpi4py'
version  = open('VERSION.txt').read().strip()
descr    = __doc__.split('\n')[1:-1]; del descr[1:3]
devstat  = ['Development Status :: 5 - Production/Stable']
url      = 'http://mpi4py.googlecode.com/'
download = url + 'files/%s-%s.tar.gz'

classifiers = """
License :: Public Domain
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
Operating System :: Microsoft :: Windows
Intended Audience :: Developers
Intended Audience :: Science/Research
Programming Language :: C
Programming Language :: Python
Programming Language :: Cython
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
    'download_url'     : download % (name, version),
    'classifiers'      : [c for c in classifiers.split('\n') if c],
    'keywords'         : [k for k in keywords.split('\n')    if k],
    'platforms'        : [p for p in platforms.split('\n')   if p],
    'provides'         : ['mpi4py', 'mpi4py.MPI',],
    'requires'         : ['pickle'],
    'license'          : 'Public Domain',
    'author'           : 'Lisandro Dalcin',
    'author_email'     : 'dalcinl@gmail.com',
    'maintainer'       : 'Lisandro Dalcin',
    'maintainer_email' : 'dalcinl@gmail.com',
    }
metadata['classifiers'] += devstat

del name, version, descr, devstat, download

# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

def ext_modules():
    import sys
    # MPI extension module
    MPI = dict(name='mpi4py.MPI',
               sources=['src/MPI.c'],
               depends=['src/mpi4py_MPI.c'],
               )
    return [MPI]

def executables():
    import sys
    from distutils import sysconfig
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
            library_dirs += cfgDict.get(var, '').split()
        if '-pthread' in cfgDict.get('LINKCC', ''):
            link_args.append('-pthread')
        for var in ('LDFLAGS',
                    'LIBS', 'MODLIBS', 'SYSLIBS',
                    'LDLAST'):
            link_args += cfgDict.get(var, '').split()

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

ExtModule = lambda extension: Extension(**extension)
ExeBinary = lambda executable: Executable(**executable)

def run_setup():
    """
    Call distutils.setup(*targs, **kwargs)
    """
    setup(packages     = ['mpi4py'],
          package_dir  = {'mpi4py' : 'src'},
          package_data = {'mpi4py' : ['include/*.pxd',
                                      'include/*.pxi',
                                      'include/mpi4py/*.h',
                                      'include/mpi4py/*.pxd',
                                      'include/mpi4py/*.pyx',
                                      'include/mpi4py/*.pxi',
                                      'include/mpi4py/*.i',]},
          ext_modules  = [ExtModule(ext) for ext in ext_modules()],
          executables  = [ExeBinary(exe) for exe in executables()],
          **metadata)

def cython_help():
    import sys, os
    if not os.path.exists(os.path.join('src', 'mpi4py_MPI.c')):
        warn = lambda msg='': sys.stderr.write(msg+'\n')
        warn("*"*70)
        warn()
        warn("You need to generate C source files with Cython !!!")
        warn("Please execute in your shell:")
        warn()
        warn("$ python ./conf/cythonize.py")
        warn()
        warn("*"*70)
        warn()

if __name__ == '__main__':
    # hack distutils.sysconfig to eliminate debug flags
    from distutils import sysconfig
    cvars = sysconfig.get_config_vars()
    cflags = cvars.get('OPT')
    if cflags:
        cflags = cflags.split()
        for flag in ('-g', '-g3'):
            if flag in cflags:
                cflags.remove(flag)
        cvars['OPT'] = str.join(' ', cflags)
    # show help about cython  ...
    cython_help()
    # and call setup
    run_setup()

# --------------------------------------------------------------------
