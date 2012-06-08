#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

"""
MPI for Python
==============

This package provides Python bindings for the **Message Passing
Interface** (MPI) standard. It is implemented on top of the
MPI-1/MPI-2 specification and exposes an API which grounds on the
standard MPI-2 C++ bindings.

This package supports:

+ Convenient communication of any *picklable* Python object

  - point-to-point (send & receive)
  - collective (broadcast, scatter & gather, reduction)

+ Fast communication of Python object exposing the *Python buffer
  interface* (NumPy arrays, builtin bytes/string/array objects)

  - point-to-point (blocking/nonbloking/persistent send & receive)
  - collective (broadcast, block/vector scatter & gather, reduction)

+ Process groups and communication domains

  - Creation of new intra/inter communicators
  - Cartesian & graph topologies

+ Parallel input/output:

  - read & write
  - blocking/nonbloking & collective/noncollective
  - individual/shared file pointers & explicit offset

+ Dynamic process management

  - spawn & spawn multiple
  - accept/connect
  - name publishing & lookup

+ One-sided operations (put, get, accumulate)

You can install the `in-development version
<hg+http://code.google.com/p/mpi4py#egg=mpi4py-dev>`_
of mpi4py with::

  $ pip install mpi4py==dev

or::

  $ easy_install mpi4py==dev
"""

## try:
##     import setuptools
## except ImportError:
##     pass

import sys, os

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

def name():
    return 'mpi4py'

def version():
    import re
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

def configure_mpi(ext, config_cmd):
    from textwrap import dedent
    from distutils import log
    from distutils.errors import DistutilsPlatformError
    #
    log.info("checking for MPI compile and link ...")
    errmsg = ("Cannot find 'mpi.h' header. "
              "Check your configuration!!!")
    ok = config_cmd.check_header("mpi.h", headers=["stdlib.h"])
    if not ok: raise DistutilsPlatformError(errmsg)
    headers = ["stdlib.h", "mpi.h"]
    ConfigTest = dedent("""\
    int main(int argc, char **argv)
    {
      (void)MPI_Init(&argc, &argv);
      (void)MPI_Finalize();
      return 0;
    }
    """)
    errmsg = ("Cannot %s MPI programs. "
              "Check your configuration!!!")
    ok = config_cmd.try_compile(ConfigTest, headers=headers)
    if not ok: raise DistutilsPlatformError(errmsg % "compile")
    ok = config_cmd.try_link(ConfigTest, headers=headers)
    if not ok: raise DistutilsPlatformError(errmsg % "link")
    #
    log.info("checking for missing MPI functions/symbols ...")
    macros = ("MPICH2 OPEN_MPI DEINO_MPI "
              "MPICH_NAME LAM_MPI "
              ).strip().split()
    ConfigTest = dedent('''\
    #if !(%s)
    #error "Unknown MPI"
    #endif ''') % "||".join(["defined(%s)" % m for m in macros])
    ok = config_cmd.try_compile(ConfigTest, headers=headers)
    if not ok:
        from conf.mpidistutils import ConfigureMPI
        configure = ConfigureMPI(config_cmd)
        results = configure.run()
        configure.dump(results)
        ext.define_macros += [('HAVE_CONFIG_H', 1)]
    else:
        for prefix, suffixes in (
            ("MPI_Type_create_f90_", ("integer", "real", "complex")),
            ):
            for suffix in suffixes:
                function = prefix + suffix
                ok = config_cmd.check_function(
                    function, decl=1, call=1)
                if not ok:
                    macro = "PyMPI_MISSING_" + function
                    ext.define_macros += [(macro, 1)]

def configure_mpe(ext, config_cmd):
    from distutils import log
    log.info("checking for MPE availability ...")
    libraries = []
    for libname in ('pthread', 'mpe', 'lmpe'):
        if config_cmd.check_library(
            libname, other_libraries=libraries):
            libraries.insert(0, libname)
    ok = (config_cmd.check_header("mpe.h",
                                  headers=["stdlib.h",
                                           "mpi.h"])
          and
          config_cmd.check_function("MPE_Init_log",
                                    headers=["stdlib.h",
                                             "mpi.h",
                                             "mpe.h"],
                                    libraries=libraries,
                                    decl=0, call=1)
          )
    if ok:
        ext.define_macros += [('HAVE_MPE', 1)]
        if ((linux or darwin or solaris) and 
            libraries[0] == 'lmpe'):
            ext.extra_link_args += whole_archive('lmpe')
            for libname in libraries[1:]:
                ext.extra_link_args += ['-l' + libname]
        else:
            ext.libraries += libraries

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
    if ok: ext.define_macros += [('HAVE_DLOPEN', 1)]

def configure_libmpe(lib, config_cmd):
    libraries = []
    for libname in ('pthread', 'mpe', 'lmpe'):
        if config_cmd.check_library(
            libname, other_libraries=libraries):
            libraries.insert(0, libname)
    if 'mpe' in libraries:
        if ((linux or darwin or solaris) and 
            libraries[0] == 'lmpe'):
            lib.extra_link_args += whole_archive('lmpe')
            for libname in libraries[1:]:
                lib.extra_link_args += ['-l' + libname]
        else:
            lib.libraries += libraries

def configure_libvt(lib, config_cmd):
    if lib.name == 'vt':
        ok = False
        for vt_lib in ('vt-mpi', 'vt.mpi'):
            ok = config_cmd.check_library(vt_lib)
            if ok: break
        if ok:
            if linux or darwin or solaris:
                lib.extra_link_args += whole_archive(vt_lib)
                lib.extra_link_args += ['-lotf', '-lz', '-ldl']
            else:
                lib.libraries += [vt_lib, 'otf', 'z', 'dl']
    elif lib.name in ('vt-mpi', 'vt-hyb'):
        vt_lib = lib.name
        ok = config_cmd.check_library(vt_lib)
        if ok: lib.libraries = [vt_lib]

def configure_pyexe(exe, config_cmd):
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


def ext_modules():
    modules = []
    # MPI extension module
    from glob import glob
    MPI = dict(
        name='mpi4py.MPI',
        sources=['src/MPI.c'],
        depends=(['src/mpi4py.MPI.c'] +
                 glob('src/*.h') +
                 glob('src/config/*.h') +
                 glob('src/compat/*.h')
                 ),
        configure=configure_mpi,
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
        configure=configure_mpe,
        )
    modules.append(MPE)
    # custom dl extension module
    dl = dict(
        name='mpi4py.dl',
        optional=True,
        sources=['src/dynload.c'],
        depends=['src/dynload.h'],
        configure=configure_dl,
        )
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
        configure=configure_libmpe,
        )
    # VampirTrace logging
    pmpi_vt = dict(
        name='vt', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/pmpi-vt.c'],
        configure=configure_libvt,
        )
    pmpi_vt_mpi = dict(
        name='vt-mpi', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/pmpi-vt-mpi.c'],
        configure=configure_libvt,
        )
    pmpi_vt_hyb = dict(
        name='vt-hyb', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/pmpi-vt-hyb.c'],
        configure=configure_libvt,
        )
    #
    return [
        pmpi_mpe,
        pmpi_vt,
        pmpi_vt_mpi,
        pmpi_vt_hyb,
        ]

def executables():
    # MPI-enabled Python interpreter
    pyexe = dict(name='python-mpi',
                 optional=True,
                 package='mpi4py',
                 dest_dir='bin',
                 sources=['src/python.c'],
                 configure=configure_pyexe,
                 )
    #
    return [pyexe]

# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------

from conf.mpidistutils import setup
from conf.mpidistutils import Extension  as Ext
from conf.mpidistutils import Library    as Lib
from conf.mpidistutils import Executable as Exe

CYTHON = '0.15'

def run_setup():
    """
    Call distutils.setup(*targs, **kwargs)
    """
    if ('setuptools' in sys.modules):
        from os.path import exists, join
        metadata['zip_safe'] = False
        if not exists(join('src', 'mpi4py.MPI.c')):
            metadata['install_requires'] = ['Cython>='+CYTHON]
    #
    setup(packages     = ['mpi4py'],
          package_dir  = {'mpi4py' : 'src'},
          package_data = {'mpi4py' : ['include/mpi4py/*.h',
                                      'include/mpi4py/*.pxd',
                                      'include/mpi4py/*.pyx',
                                      'include/mpi4py/*.pxi',
                                      'include/mpi4py/*.i',
                                      'MPI.pxd', 'mpi_c.pxd',]},
          ext_modules  = [Ext(**ext) for ext in ext_modules()],
          libraries    = [Lib(**lib) for lib in libraries()  ],
          executables  = [Exe(**exe) for exe in executables()],
          **metadata)

def chk_cython(VERSION):
    CYTHON_VERSION_REQUIRED = VERSION
    from distutils import log
    from distutils.version import StrictVersion as Version
    warn = lambda msg='': sys.stderr.write(msg+'\n')
    #
    cython_zip = 'cython.zip'
    if os.path.isfile(cython_zip):
        path = os.path.abspath(cython_zip)
        if sys.path[0] != path:
            sys.path.insert(0, path)
            log.info("adding '%s' to sys.path", cython_zip)
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
    if (CYTHON_VERSION_REQUIRED is not None and
        Version(CYTHON_VERSION) < Version(CYTHON_VERSION_REQUIRED)):
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

def run_cython(source, depends=(), includes=(),
               destdir_c=None, destdir_h=None,
               wdir=None, force=False, VERSION=None):
    from glob import glob
    from distutils import log
    from distutils import dep_util
    from distutils.errors import DistutilsError
    target = os.path.splitext(source)[0]+".c"
    cwd = os.getcwd()
    try:
        if wdir: os.chdir(wdir)
        alldeps = [source]
        for dep in depends:
            alldeps += glob(dep)
        if not (force or dep_util.newer_group(alldeps, target)):
            log.debug("skipping '%s' -> '%s' (up-to-date)",
                      source, target)
            return
    finally:
        os.chdir(cwd)
    if not chk_cython(VERSION):
        raise DistutilsError('requires Cython>=%s' % VERSION)
    log.info("cythonizing '%s' -> '%s'", source, target)
    from conf.cythonize import cythonize
    err = cythonize(source,
                    includes=includes,
                    destdir_c=destdir_c,
                    destdir_h=destdir_h,
                    wdir=wdir)
    if err:
        raise DistutilsError(
            "Cython failure: '%s' -> '%s'" % (source, target))

def build_sources(cmd):
    from distutils.errors import DistutilsError
    from os.path import exists, isdir, join
    has_src = (exists(join('src', 'mpi4py.MPI.c')) and
               exists(join('src', 'mpi4py.MPE.c')))
    has_vcs = (isdir('.hg') or isdir('.git') or isdir('.svn'))
    if (has_src and not has_vcs and not cmd.force): return
    # mpi4py.MPI
    source = 'mpi4py.MPI.pyx'
    depends = ("include/*/*.pxi",
               "include/*/*.pxd",
               "MPI/*.pyx",
               "MPI/*.pxi",)
    includes = ['include']
    destdir_h = os.path.join('include', 'mpi4py')
    run_cython(source, depends, includes,
               destdir_c=None, destdir_h=destdir_h,
               wdir='src', force=cmd.force, VERSION=CYTHON)
    # mpi4py.MPE
    source = 'mpi4py.MPE.pyx'
    depends = ("MPE/*.pyx",
               "MPE/*.pxi",)
    includes = ['include']
    run_cython(source, depends, includes,
               destdir_c=None, destdir_h=None,
               wdir='src', force=cmd.force, VERSION=CYTHON)

from conf.mpidistutils import build_src
build_src.run = build_sources

def run_testsuite(cmd):
    from distutils.errors import DistutilsError
    sys.path.insert(0, 'test')
    try:
        from runtests import main
    finally:
        del sys.path[0]
    err = main(cmd.args or [])
    if err:
        raise DistutilsError("test")

from conf.mpidistutils import test
test.run = run_testsuite

def main():
    run_setup()

if __name__ == '__main__':
    main()

# --------------------------------------------------------------------
