#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

__doc__ = \
"""
Python bindings for MPI
"""

import sys
import os
import re

try:
    import setuptools
except ImportError:
    setuptools = None

pyver = sys.version_info[:2]
if pyver < (2, 6) or (3, 0) <= pyver < (3, 2):
    raise RuntimeError("Python version 2.6, 2.7 or >= 3.2 required")
if pyver == (2, 6) or pyver == (3, 2):
    sys.stderr.write(
        "WARNING: Python %d.%d is not supported.\n" % pyver)
if (hasattr(sys, 'pypy_version_info') and
    sys.pypy_version_info[:2] < (2, 0)):
    raise RuntimeError("PyPy version >= 2.0 required")

topdir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(topdir, 'conf'))

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

def name():
    return 'mpi4py'

def version():
    srcdir = os.path.join(topdir, 'src')
    with open(os.path.join(srcdir, 'mpi4py', '__init__.py')) as f:
        m = re.search(r"__version__\s*=\s*'(.*)'", f.read())
        return m.groups()[0]

def description():
    with open(os.path.join(topdir, 'DESCRIPTION.rst')) as f:
        return f.read()

name    = name()
version = version()

url      = 'https://bitbucket.org/mpi4py/%(name)s/' % vars()
download = url + 'downloads/%(name)s-%(version)s.tar.gz' % vars()

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
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Distributed Computing
"""

keywords = """
scientific computing
parallel computing
message passing interface
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
    'description'      : __doc__.strip(),
    'long_description' : description(),
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

metadata['provides'] = ['mpi4py']

# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

def run_command(exe, args):
    from distutils.spawn import find_executable
    from distutils.util  import split_quoted
    cmd = find_executable(exe)
    if not cmd: return []
    if not isinstance(args, str):
        args = ' '.join(args)
    try:
        with os.popen(cmd + ' ' + args) as f:
            return split_quoted(f.read())
    except:
        return []

linux   = sys.platform.startswith('linux')
solaris = sys.platform.startswith('sunos')
darwin  = sys.platform.startswith('darwin')

if linux:
    def whole_archive(compiler, name, library_dirs=[]):
        return ['-Wl,-whole-archive',
                '-l' + name,
                '-Wl,-no-whole-archive',
                ]
elif darwin:
    def darwin_linker_dirs(compiler):
        from distutils.util import split_quoted
        linker_cmd = compiler.linker_so + ['-show']
        linker_cmd = run_command(linker_cmd[0], linker_cmd[1:])
        library_dirs  = compiler.library_dirs[:]
        library_dirs += [flag[2:] for flag in linker_cmd
                         if flag.startswith('-L')]
        library_dirs += ['/usr/lib']
        library_dirs += ['/usr/local/lib']
        return library_dirs
    def whole_archive(compiler, name, library_dirs=[]):
        library_dirs = library_dirs[:]
        library_dirs += darwin_linker_dirs(compiler)
        for libdir in library_dirs:
            libpath = os.path.join(libdir, 'lib%s.a' % name)
            if os.path.isfile(libpath):
                return ['-force_load', libpath]
        return ['-l%s' % name]
elif solaris:
    def whole_archive(compiler, name, library_dirs=[]):
        return ['-Wl,-zallextract',
                '-l' + name,
                '-Wl,-zdefaultextract',
                ]
else:
    whole_archive = None

def configure_dl(ext, config_cmd):
    from distutils import log
    log.info("checking for dlopen() availability ...")
    ok = config_cmd.check_header('dlfcn.h')
    if ok : ext.define_macros += [('HAVE_DLFCN_H', 1)]
    ok = config_cmd.check_library('dl')
    if ok: ext.libraries += ['dl']
    ok = config_cmd.check_function('dlopen',
                                   libraries=['dl'],
                                   decl=1, call=1)
    if ok: ext.define_macros += [('HAVE_DLOPEN', 1)]

def configure_mpi(ext, config_cmd):
    from textwrap import dedent
    from distutils import log
    from distutils.errors import DistutilsPlatformError
    headers = ['stdlib.h', 'mpi.h']
    #
    log.info("checking for MPI compile and link ...")
    ConfigTest = dedent("""\
    int main(int argc, char **argv)
    {
      (void)MPI_Init(&argc, &argv);
      (void)MPI_Finalize();
      return 0;
    }
    """)
    errmsg = "Cannot %s MPI programs. Check your configuration!!!"
    ok = config_cmd.try_compile(ConfigTest, headers=headers)
    if not ok: raise DistutilsPlatformError(errmsg % "compile")
    ok = config_cmd.try_link(ConfigTest, headers=headers)
    if not ok: raise DistutilsPlatformError(errmsg % "link")
    #
    log.info("checking for missing MPI functions/symbols ...")
    tests  = ["defined(%s)" % macro for macro in
              ("OPEN_MPI", "MSMPI_VER",)]
    tests += ["(defined(MPICH_NAME)&&(MPICH_NAME==3))"]
    tests += ["(defined(MPICH_NAME)&&(MPICH_NAME==2))"]
    ConfigTest = dedent("""\
    #if !(%s)
    #error "Unknown MPI implementation"
    #endif
    """) % "||".join(tests)
    ok = config_cmd.try_compile(ConfigTest, headers=headers)
    if not ok:
        from mpidistutils import ConfigureMPI
        configure = ConfigureMPI(config_cmd)
        results = configure.run()
        configure.dump(results)
        ext.define_macros += [('HAVE_CONFIG_H', 1)]
    else:
        for function, arglist in (
            ('MPI_Type_create_f90_integer',   '0,(MPI_Datatype*)0'),
            ('MPI_Type_create_f90_real',    '0,0,(MPI_Datatype*)0'),
            ('MPI_Type_create_f90_complex', '0,0,(MPI_Datatype*)0'),
            ('MPI_Status_c2f', '(MPI_Status*)0,(MPI_Fint*)0'),
            ('MPI_Status_f2c', '(MPI_Fint*)0,(MPI_Status*)0'),
            ):
            ok = config_cmd.check_function_call(
                function, arglist, headers=headers)
            if not ok:
                macro = 'PyMPI_MISSING_' + function
                ext.define_macros += [(macro, 1)]
    #
    if os.name == 'posix':
        configure_dl(ext, config_cmd)

def configure_libmpe(lib, config_cmd):
    #
    mpecc = os.environ.get('MPECC') or 'mpecc'
    command = run_command(mpecc, '-mpilog -show')
    for arg in command:
        if arg.startswith('-L'):
            libdir = arg[2:]
            lib.library_dirs.append(libdir)
            lib.runtime_library_dirs.append(libdir)
    #
    log_lib  = 'lmpe'
    dep_libs = ('pthread', 'mpe')
    ok = config_cmd.check_library(log_lib, lib.library_dirs)
    if not ok: return
    libraries = []
    for libname in dep_libs:
        if config_cmd.check_library(
            libname, lib.library_dirs,
            other_libraries=libraries):
            libraries.insert(0, libname)
    if whole_archive:
        cc = config_cmd.compiler
        dirs = lib.library_dirs[:]
        lib.extra_link_args += whole_archive(cc, log_lib, dirs)
        lib.extra_link_args += ['-l' + libname
                                for libname in libraries]
    else:
        lib.libraries += [log_lib] + libraries

def configure_libvt(lib, config_cmd):
    #
    vtcc = os.environ.get('VTCC') or 'vtcc'
    command = run_command(vtcc, '-vt:showme')
    for arg in command:
        if arg.startswith('-L'):
            libdir = arg[2:]
            lib.library_dirs.append(libdir)
            lib.runtime_library_dirs.append(libdir)
    # modern VampirTrace
    if lib.name == 'vt':
        log_lib = 'vt-mpi'
    else:
        log_lib = lib.name
    ok = config_cmd.check_library(log_lib, lib.library_dirs)
    if ok: lib.libraries = [log_lib]
    if ok: return
    # older VampirTrace, Open MPI <= 1.4
    if lib.name == 'vt-hyb':
        log_lib = 'vt.ompi'
    else:
        log_lib = 'vt.mpi'
    dep_libs = ('dl', 'z', 'otf',)
    ok = config_cmd.check_library(log_lib, lib.library_dirs)
    if not ok: return
    libraries = []
    for libname in dep_libs:
        if config_cmd.check_library(
            libname, lib.library_dirs,
            other_libraries=libraries):
            libraries.insert(0, libname)
    if whole_archive:
        cc = config_cmd.compiler
        dirs = lib.library_dirs[:]
        lib.extra_link_args += whole_archive(cc, log_lib, dirs)
        lib.extra_link_args += ['-l' + libname
                                for libname in libraries]
    else:
        lib.libraries += [log_lib] + libraries
    lib.define_macros.append(('LIBVT_LEGACY', 1))
    if lib.name == 'vt-hyb':
        openmp_flag = '-fopenmp' # GCC, Intel
        lib.extra_compile_args.append(openmp_flag)
        lib.extra_link_args.append(openmp_flag)

def configure_pyexe(exe, config_cmd):
    from distutils import sysconfig
    if sys.platform.startswith('win'):
        return
    if (sys.platform == 'darwin' and
        ('Anaconda' in sys.version or
         'Continuum Analytics' in sys.version)):
        py_version = sysconfig.get_python_version()
        py_abiflags = getattr(sys, 'abiflags', '')
        exe.libraries += ['python' + py_version + py_abiflags]
        return
    #
    from distutils.util import split_quoted
    cfg_vars = sysconfig.get_config_vars()
    libraries = []
    library_dirs = []
    link_args = []
    if not sysconfig.get_config_var('Py_ENABLE_SHARED'):
        py_version = sysconfig.get_python_version()
        py_abiflags = getattr(sys, 'abiflags', '')
        libraries = ['python' + py_version + py_abiflags]
        if hasattr(sys, 'pypy_version_info'):
            py_tag = py_version[0].replace('2', '')
            libraries = ['pypy%s-c' % py_tag]
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
    # MPI extension module
    from glob import glob
    MPI = dict(
        name='mpi4py.MPI',
        sources=['src/MPI.c'],
        depends=(['src/mpi4py.MPI.c'] +
                 glob('src/*.h') +
                 glob('src/lib-mpi/*.h') +
                 glob('src/lib-mpi/config/*.h') +
                 glob('src/lib-mpi/compat/*.h')
                 ),
        configure=configure_mpi,
        )
    modules.append(MPI)
    #
    return modules

def libraries():
    # MPE logging
    pmpi_mpe = dict(
        name='mpe', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/lib-pmpi/mpe.c'],
        configure=configure_libmpe,
        )
    # VampirTrace logging
    pmpi_vt = dict(
        name='vt', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/lib-pmpi/vt.c'],
        configure=configure_libvt,
        )
    pmpi_vt_mpi = dict(
        name='vt-mpi', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/lib-pmpi/vt-mpi.c'],
        configure=configure_libvt,
        )
    pmpi_vt_hyb = dict(
        name='vt-hyb', kind='dylib',
        optional=True,
        package='mpi4py',
        dest_dir='lib-pmpi',
        sources=['src/lib-pmpi/vt-hyb.c'],
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
    if hasattr(sys, 'pypy_version_info'):
        return []
    return [pyexe]

# --------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------

from mpidistutils import setup
from mpidistutils import Extension  as Ext
from mpidistutils import Library    as Lib
from mpidistutils import Executable as Exe

CYTHON = '0.22'

def run_setup():
    """
    Call setup(*args, **kargs)
    """
    setup_args = metadata.copy()
    if setuptools:
        setup_args['zip_safe'] = False
    if setuptools and not os.getenv('CONDA_BUILD'):
        src = os.path.join('src', 'mpi4py.MPI.c')
        has_src = os.path.exists(os.path.join(topdir, src))
        has_git = os.path.isdir(os.path.join(topdir, '.git'))
        has_hg  = os.path.isdir(os.path.join(topdir, '.hg'))
        if not has_src or has_git or has_hg:
            setup_args['setup_requires'] = ['Cython>='+CYTHON]
    #
    setup(packages     = ['mpi4py', 'mpi4py.futures'],
          package_dir  = {'mpi4py' : 'src/mpi4py'},
          package_data = {'mpi4py' : ['*.pxd',
                                      'include/mpi4py/*.h',
                                      'include/mpi4py/*.i',
                                      'include/mpi4py/*.pxi',]},
          ext_modules  = [Ext(**ext) for ext in ext_modules()],
          libraries    = [Lib(**lib) for lib in libraries()  ],
          executables  = [Exe(**exe) for exe in executables()],
          **setup_args)

def chk_cython(VERSION):
    from distutils import log
    from distutils.version import LooseVersion
    from distutils.version import StrictVersion
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
    REQUIRED = VERSION
    m = re.match(r"(\d+\.\d+(?:\.\d+)?).*", CYTHON_VERSION)
    if m:
        Version = StrictVersion
        AVAILABLE = m.groups()[0]
    else:
        Version = LooseVersion
        AVAILABLE = CYTHON_VERSION
    if (REQUIRED is not None and
        Version(AVAILABLE) < Version(REQUIRED)):
        warn("*"*80)
        warn()
        warn(" You need to install Cython %s (you have version %s)"
             % (REQUIRED, CYTHON_VERSION))
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
    target = os.path.splitext(source)[0]+'.c'
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
        raise DistutilsError("requires Cython>=%s" % VERSION)
    log.info("cythonizing '%s' -> '%s'", source, target)
    from cythonize import cythonize
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
    has_src = os.path.exists(os.path.join(
        topdir, 'src', 'mpi4py.MPI.c'))
    has_vcs = (os.path.isdir(os.path.join(topdir, '.git')) or
               os.path.isdir(os.path.join(topdir, '.hg' )))
    if (has_src and not has_vcs and not cmd.force): return
    # mpi4py.MPI
    source = 'mpi4py.MPI.pyx'
    depends = ['mpi4py/MPI/*.pyx',
               'mpi4py/MPI/*.pxd',
               'mpi4py/MPI/*.pxi',]
    destdir_h = os.path.join('mpi4py', 'include', 'mpi4py')
    run_cython(source, depends, destdir_h=destdir_h,
               wdir='src', force=cmd.force, VERSION=CYTHON)

from mpidistutils import build_src
build_src.run = build_sources

def run_testsuite(cmd):
    from distutils.errors import DistutilsError
    sys.path.insert(0, 'test')
    try:
        from runtests import main
    finally:
        del sys.path[0]
    if cmd.dry_run:
        return
    args = cmd.args[:] or []
    if cmd.verbose < 1:
        args.insert(0,'-q')
    if cmd.verbose > 1:
        args.insert(0,'-v')
    err = main(args)
    if err:
        raise DistutilsError("test")

from mpidistutils import test
test.run = run_testsuite

def main():
    run_setup()

if __name__ == '__main__':
    main()

# --------------------------------------------------------------------
