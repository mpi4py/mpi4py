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
import shlex
import shutil
from glob import glob

try:
    import setuptools
except ImportError:
    setuptools = None

if sys.version_info < (3, 6):
    raise RuntimeError("Python version 3.6+ required")

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
    public_version = m.groups()[0]
    local_version = os.environ.get('MPI4PY_LOCAL_VERSION')
    if local_version:
        return '{0}+{1}'.format(public_version, local_version)
    else:
        return public_version

def description():
    with open(os.path.join(topdir, 'DESCRIPTION.rst')) as f:
        return f.read()

name    = name()
version = version()

url      = 'https://github.com/mpi4py/%(name)s/' % vars()
download = url + 'releases/download/%(version)s/' % vars()
download = download + '%(name)s-%(version)s.tar.gz' % vars()

classifiers = """
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Operating System :: MacOS
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: BSD
Operating System :: POSIX :: Linux
Operating System :: Unix
Programming Language :: C
Programming Language :: Cython
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
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
POSIX
Linux
macOS
FreeBSD
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

def configure_dl(ext, config_cmd):
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
    from mpidistutils import DistutilsPlatformError
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
    tests += ["(defined(MPICH_NAME)&&(MPICH_NAME>=3))"]
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
        for symbol, stype in (
            ('MPI_LB', 'MPI_Datatype'),
            ('MPI_UB', 'MPI_Datatype'),
            ):
            ok = config_cmd.check_symbol(
                symbol, type=stype, headers=headers)
            if not ok:
                macro = 'PyMPI_MISSING_' + symbol
                ext.define_macros += [(macro, 1)]
    #
    if os.name == 'posix':
        configure_dl(ext, config_cmd)

def configure_pyexe(exe, config_cmd):
    from mpidistutils import sysconfig
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
    pyver = sys.version_info[:2]
    cfg_vars = sysconfig.get_config_vars()
    libraries = []
    library_dirs = []
    runtime_dirs = []
    link_args = []
    if pyver >= (3, 8) or not cfg_vars.get('Py_ENABLE_SHARED'):
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
        library_dirs += shlex.split(cfg_vars.get(var, ''))
    for var in ('LIBDIR',):
        runtime_dirs += shlex.split(cfg_vars.get(var, ''))
    for var in ('LIBS', 'MODLIBS', 'SYSLIBS', 'LDLAST'):
        link_args += shlex.split(cfg_vars.get(var, ''))
    exe.libraries += libraries
    exe.library_dirs += library_dirs
    exe.runtime_library_dirs += runtime_dirs
    exe.extra_link_args += link_args


def extensions():
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
    MPI = dict(
        name='mpi4py.MPI',
        sources=['src/MPI.c'],
        depends=(
            ['src/mpi4py.MPI.c'] +
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

from mpidistutils import log
from mpidistutils import setup
from mpidistutils import Extension  as Ext
from mpidistutils import Executable as Exe

CYTHON = '0.27'

def run_setup():
    """
    Call setup(*args, **kargs)
    """
    setup_args = metadata.copy()
    if setuptools:
        setup_args['zip_safe'] = False
        setup_args['setup_requires'] = []
        setup_args['python_requires'] = '>=3.6'
    if setuptools and not os.getenv('CONDA_BUILD'):
        src = os.path.join('src', 'mpi4py.MPI.c')
        has_src = os.path.exists(os.path.join(topdir, src))
        has_git = os.path.isdir(os.path.join(topdir, '.git'))
        has_hg  = os.path.isdir(os.path.join(topdir, '.hg'))
        if not has_src or has_git or has_hg:
            setup_args['setup_requires'] += ['Cython>='+CYTHON]
    #
    setup(
        packages = [
            'mpi4py',
            'mpi4py.futures',
            'mpi4py.util',
        ],
        package_data = {
            'mpi4py' : [
                '*.pxd',
                'include/mpi4py/*.h',
                'include/mpi4py/*.i',
                'include/mpi4py/*.pxi',
            ],
            '' : [
                'py.typed',
                '*.pyi',
            ],
        },
        package_dir = {'' : 'src'},
        ext_modules = [Ext(**ext) for ext in extensions()],
        executables = [Exe(**exe) for exe in executables()],
        **setup_args
    )

def chk_cython(VERSION):
    warn = lambda msg='': sys.stderr.write(msg+'\n')
    #
    try:
        import Cython
    except ImportError:
        warn("*"*80)
        warn()
        warn(" You need to generate C source files with Cython!!")
        warn(" Download and install Cython <https://cython.org>")
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
        from mpidistutils import Version
        AVAILABLE = m.groups()[0]
    else:
        from mpidistutils import LegacyVersion as Version
        AVAILABLE = CYTHON_VERSION
    if (REQUIRED is not None and
        Version(AVAILABLE) < Version(REQUIRED)):
        warn("*"*80)
        warn()
        warn(" You need to install Cython %s (you have version %s)"
             % (REQUIRED, CYTHON_VERSION))
        warn(" Download and install Cython <https://cython.org>")
        warn()
        warn("*"*80)
        return False
    #
    log.info("using Cython version %s" % CYTHON_VERSION)
    return True

def run_cython(source, target=None,
               depends=(), includes=(),
               destdir_c=None, destdir_h=None,
               wdir=None, force=False, VERSION=None):
    from mpidistutils import dep_util
    from mpidistutils import DistutilsError
    if target is None:
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
    err = cythonize(source, target,
                    includes=includes,
                    destdir_c=destdir_c,
                    destdir_h=destdir_h,
                    wdir=wdir)
    if err:
        raise DistutilsError(
            "Cython failure: '%s' -> '%s'" % (source, target))

def build_sources(cmd):
    has_src = os.path.exists(os.path.join(
        topdir, 'src', 'mpi4py.MPI.c'))
    has_vcs = (os.path.isdir(os.path.join(topdir, '.git')) or
               os.path.isdir(os.path.join(topdir, '.hg' )))
    if (has_src and not has_vcs and not cmd.force): return
    # mpi4py.MPI
    source = 'mpi4py/MPI.pyx'
    target = 'mpi4py.MPI.c'
    depends = [
        'mpi4py/*.pyx',
        'mpi4py/*.pxd',
        'mpi4py/MPI/*.pyx',
        'mpi4py/MPI/*.pxd',
        'mpi4py/MPI/*.pxi',
    ]
    destdir_h = os.path.join('mpi4py', 'include', 'mpi4py')
    run_cython(source, target, depends, destdir_h=destdir_h,
               wdir='src', force=cmd.force, VERSION=CYTHON)

from mpidistutils import build_src
build_src.run = build_sources

def main():
    run_setup()

if __name__ == '__main__':
    main()

# --------------------------------------------------------------------
