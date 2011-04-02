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

## try:
##     import setuptools
## except ImportError:
##     pass

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

def name():
    return 'mpi4py'

def version():
    import os, re
    fh = open(os.path.join('src', '__init__.py'))
    try: data = fh.read()
    finally: fh.close()
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

import sys
linux   = sys.platform.startswith('linux')
solaris = sys.platform.startswith('sunos')
darwin  = sys.platform.startswith('darwin')
if linux:
    def whole_archive(name):
        return ['-Wl,-whole-archive',
                '-l%s' % name,
                '-Wl,-no-whole-archive',
                ]
elif darwin:
    def whole_archive(name):
        return [#'-Wl,-force_load',
                '-l%s' % name,
                ]
elif solaris:
    def whole_archive(name):
        return ['-Wl,-zallextract',
                '-l%s' % name,
                '-Wl,-zdefaultextract',
                ]
else:
    def whole_archive(name):
        return ['-l%s' % name]

def ext_modules():
    import sys, os
    modules = []
    # MPI extension module
    MPI = dict(
        name='mpi4py.MPI',
        sources=['src/MPI.c'],
        depends=['src/mpi4py.MPI.c'],
        )
    def configure_mpi(ext, config_cmd):
        from distutils import log
        log.info("checking for MPI compile and link ...")
        config_cmd.check_header("mpi.h", headers=["stdlib.h"])
        config_cmd.check_function("MPI_Finalize", decl=0, call=1,
                                  headers=['stdlib.h', 'mpi.h'])
        ConfigTest = """\
        int main(int argc, char **argv)
        {
          int ierr;
          ierr = MPI_Init(&argc, &argv);
          ierr = MPI_Finalize();
          return 0;
        }
        """
        ok = config_cmd.try_link(ConfigTest,
                                 headers=['stdlib.h', 'mpi.h'])
        if not ok:
            raise DistutilsPlatformError(
                "Cannot compile/link MPI programs. "
                "Check your configuration!!!")
    
    MPI['configure'] = configure_mpi
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
        )
    def configure_mpe(ext, config_cmd):
        from distutils import log
        log.info("checking for MPE availability ...")
        ok = (config_cmd.check_header("mpe.h",
                                      headers=["stdlib.h",
                                               "mpi.h",])
              and
              config_cmd.check_library('mpe')
              and
              config_cmd.check_function("MPE_Init_log",
                                        headers=["stdlib.h",
                                                 "mpi.h",
                                                 "mpe.h"],
                                        libraries=['mpe'],
                                        decl=0, call=1)
              )
        if ok:
            ext.define_macros += [('HAVE_MPE', 1)]
            if linux or darwin or solaris:
                ext.extra_link_args +=  whole_archive('lmpe')
                ext.extra_link_args +=  ['-lmpe']
            else:
                ext.libraries += ['mpe']
            return None
    MPE['configure'] = configure_mpe
    modules.append(MPE)
    # custom dl extension module
    dl = dict(
        name='mpi4py.dl',
        optional=True,
        sources=['src/dynload.c'],
        depends=['src/dynload.h'],
        )
    def configure_dl(ext, config_cmd):
        from distutils import log
        log.info("checking for dlopen() availability ...")
        ok = config_cmd.check_header("dlfcn.h")
        if ok : ext.define_macros += [('HAVE_DLFCN_H', 1)]
        ok = config_cmd.check_library('dl')
        if ok: ext.libraries += ['dl']
        ok = config_cmd.check_function("dlopen",
                                       libraries=['dl'],
                                       decl=1, call=1)
        #if ok : ext.define_macros += [('HAVE_DLOPEN', 1)]
    dl['configure'] = configure_dl
    if os.name == 'posix':
        modules.append(dl)
    #
    return modules

def libraries():
    # MPE logging
    pmpi_mpe = dict(
        name='mpe', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/pmpi-mpe.c'],
        )
    def configure_mpe(lib, config_cmd):
        ok = config_cmd.check_library('mpe')
        if ok:
            if linux or darwin or solaris:
                lib.extra_link_args += whole_archive('lmpe')
                lib.extra_link_args += ['-lmpe']
            else:
                lib.libraries += ['mpe']
        return None
    pmpi_mpe['configure'] = configure_mpe
    # VampirTrace logging
    pmpi_vt = dict(
        name='vt', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/pmpi-vt.c'],
        )
    pmpi_vt_mpi = dict(
        name='vt-mpi', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/pmpi-vt-mpi.c'],
        )
    pmpi_vt_hyb = dict(
        name='vt-hyb', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/pmpi-vt-hyb.c'],
        )
    def configure_vt(lib, config_cmd):
        if lib.name == 'vt':
            ok = False
            for vt_lib in ('vt-mpi', 'vt.mpi'):
                ok = config_cmd.check_library(vt_lib)
                if ok: break
            if ok:
                if linux or darwin or solaris:
                    lib.extra_link_args += \
                        whole_archive(vt_lib)
                    lib.extra_link_args += \
                        ['-lotf', '-lz', '-ldl']
                else:
                    lib.libraries += \
                        [vt_lib, 'otf', 'z', 'dl'],
        elif lib.name in ('vt-mpi', 'vt-hyb'):
            vt_lib = lib.name
            ok = config_cmd.check_library(vt_lib)
            if ok: lib.libraries = [vt_lib]
        return None
    pmpi_vt['configure']     = configure_vt
    pmpi_vt_mpi['configure'] = configure_vt
    pmpi_vt_hyb['configure'] = configure_vt
    #
    return [
        pmpi_mpe,
        pmpi_vt,
        pmpi_vt_mpi,
        pmpi_vt_hyb,
        ]

def executables():
    import sys
    # MPI-enabled Python interpreter
    pyexe = dict(name='python%s-mpi' % sys.version[:3],
                 optional=True,
                 #package='mpi4py',
                 #dest_dir='bin',
                 sources=['src/python.c'],
                 )
    def configure_exe(exe, config_cmd):
        import sys
        from distutils import sysconfig
        from distutils.util import split_quoted
        if sys.platform.startswith('win'):
            return
        libraries = []
        library_dirs = []
        link_args = []
        if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
            py_version = sysconfig.get_python_version()
            py_abiflags = getattr(sys, 'abiflags', '')
            libraries = ['python' + py_version + py_abiflags]
        cfg_vars = sysconfig.get_config_vars()
        if sys.platform == 'darwin':
            fwkdir = cfg_vars.get('PYTHONFRAMEWORKDIR')
            if (fwkdir and fwkdir != 'no-framework' and
                fwkdir in cfg_vars.get('LINKFORSHARED', '')):
                del libraries[:]
        for var in ('LIBDIR', 'LIBPL'):
            library_dirs += split_quoted(cfg_vars.get(var, ''))
        for var in ('LDFLAGS', 
                    'LIBS', 'MODLIBS', 'SYSLIBS',
                    'LDLAST'):
            link_args += split_quoted(cfg_vars.get(var, ''))
            
        exe.libraries += libraries
        exe.library_dirs += library_dirs
        exe.extra_link_args += link_args
    #
    pyexe['configure'] = configure_exe
    return [pyexe]

# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------

from conf.mpidistutils import setup
from conf.mpidistutils import Distribution, Extension
from conf.mpidistutils import Library, Executable
from conf.mpidistutils import config, build, install, clean
from conf.mpidistutils import build_src, build_ext, build_exe
from conf.mpidistutils import install_data, install_exe

Ext = Extension
Lib = Library
Exe = Executable

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
          ext_modules  = [Ext(**ext) for ext in ext_modules()],
          libraries    = [Lib(**lib) for lib in libraries()  ],
          executables  = [Exe(**exe) for exe in executables()],
          **metadata)

def chk_cython(CYTHON_VERSION_REQUIRED):
    import sys, os
    from distutils.version import StrictVersion as Version
    warn = lambda msg='': sys.stderr.write(msg+'\n')
    #
    try:
        import Cython
    except ImportError:
        warn("*"*80)
        warn()
        warn(" You need to generate C source files with Cython!!")
        warn(" Download and install Cython <http://www.cython.org>")
        warn()
        warn("*"*80)
        return False
    #
    try:
        CYTHON_VERSION = Cython.__version__
    except AttributeError:
        from Cython.Compiler.Version import version as CYTHON_VERSION
    CYTHON_VERSION = CYTHON_VERSION.split('+', 1)[0]
    for s in ('.alpha', 'alpha'):
        CYTHON_VERSION = CYTHON_VERSION.replace(s, 'a')
    for s in ('.beta',  'beta', '.rc', 'rc', '.c', 'c'):
        CYTHON_VERSION = CYTHON_VERSION.replace(s, 'b')
    if Version(CYTHON_VERSION) < Version(CYTHON_VERSION_REQUIRED):
        warn("*"*80)
        warn()
        warn(" You need to install Cython %s (you have version %s)"
             % (CYTHON_VERSION_REQUIRED, CYTHON_VERSION))
        warn(" Download and install Cython <http://www.cython.org>")
        warn()
        warn("*"*80)
        return False
    #
    return True

def run_cython(source, target, depends=(), force=False,
               CYTHON_VERSION_REQUIRED=None):
    from distutils import log
    from distutils import dep_util
    from distutils.errors import DistutilsError
    depends = [source] + list(depends)
    if not (force or dep_util.newer_group(depends, target)):
        log.debug("skipping '%s' -> '%s' (up-to-date)", 
                  source, target)
        return
    if (CYTHON_VERSION_REQUIRED and not 
        chk_cython(CYTHON_VERSION_REQUIRED)):
        raise DistutilsError('requires Cython>=%s' 
                             % CYTHON_VERSION_REQUIRED)
    log.info("cythonizing '%s' -> '%s'", source, target)
    from conf.cythonize import run as cythonize
    cythonize(source)

def build_sources(cmd):
    CYTHON_VERSION_REQUIRED = '0.13'
    import os, glob
    if not (os.path.isdir('.svn') or 
            os.path.isdir('.git') or
            cmd.force): return
    # mpi4py.MPI
    source = os.path.join('src', 'mpi4py.MPI.pyx')
    target = os.path.splitext(source)[0]+".c"
    depends = (glob.glob("src/include/*/*.pxi") +
               glob.glob("src/include/*/*.pxd") +
               glob.glob("src/MPI/*.pyx") +
               glob.glob("src/MPI/*.pxi"))
    run_cython(source, target, depends, cmd.force,
               CYTHON_VERSION_REQUIRED)
    # mpi4py.MPE
    source = os.path.join('src', 'mpi4py.MPE.pyx')
    target = os.path.splitext(source)[0]+".c"
    depends = (glob.glob("src/MPE/*.pyx") +
               glob.glob("src/MPE/*.pxi"))
    run_cython(source, target, depends, cmd.force,
               CYTHON_VERSION_REQUIRED)

build_src.run = build_sources

def main():
    run_setup()

if __name__ == '__main__':
    main()

# --------------------------------------------------------------------
