#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

__doc__ = \
"""
Python bindings for MPI
"""

import os
import re
import sys
import glob
import shlex
import shutil

topdir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(topdir, 'conf'))

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

def get_name():
    return 'mpi4py'

def get_version():
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
    return __doc__.strip()

def long_description():
    filelist = ('DESCRIPTION.rst', 'CITATION.rst', 'INSTALL.rst')
    template = "See `{0} <{0}>`_.\n\n"
    template += ".. include:: {0}\n"
    text = template.format(filelist[0])
    for filename in filelist:
        with open(os.path.join(topdir, filename)) as f:
            includeline = template.format(filename)
            text = text.replace(includeline, f.read())
    return text

def homepage():
    return 'https://mpi4py.github.io'

def github(*args):
    base = 'https://github.com/mpi4py/mpi4py'
    return '/'.join((base,) + args)

def readthedocs(*args):
    base = 'https://mpi4py.readthedocs.io'
    return '/'.join((base,) + args)

def download_url():
    if '.dev' in version:
        path = 'tarball'
        archive = 'master'
    else:
        path = 'releases/download/' + version
        archive = name + '-' + version + '.tar.gz'
    return github(path, archive)

def documentation_url():
    language = 'en'
    location = 'latest' if '.dev' in version else version
    return readthedocs(language, location, '')

name = get_name()
version = get_version()

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
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
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
    'description'      : description(),
    'long_description' : long_description(),
    'url'              : homepage(),
    'download_url'     : download_url(),
    'classifiers'      : classifiers.strip().split('\n'),
    'keywords'         : keywords.strip().split('\n'),
    'platforms'        : platforms.strip().split('\n'),
    'license'          : 'BSD-2-Clause',
    'author'           : 'Lisandro Dalcin',
    'author_email'     : 'dalcinl@gmail.com',
}

require_python = (3, 6)

metadata_extra = {
    'project_urls': {
        "Source Code"   : github(),
        "Bug Tracker"   : github('issues'),
        "Discussions"   : github('discussions'),
        "Documentation" : documentation_url(),
    },
    'python_requires': '>=' + '.'.join(map(str, require_python)),
    'long_description_content_type': 'text/rst',
}

# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------


def configure_dl(ext, config_cmd):
    from mpidistutils import log
    log.info("checking for dlopen() availability ...")
    dlfcn = config_cmd.check_header('dlfcn.h')
    libdl = config_cmd.check_library('dl')
    libs = ['dl'] if libdl else None
    dlopen = config_cmd.check_function(
        'dlopen', libraries=libs, decl=1, call=1,
    )
    if dlfcn:
        ext.define_macros += [('HAVE_DLFCN_H', 1)]
    if dlopen:
        ext.define_macros += [('HAVE_DLOPEN', 1)]


def configure_mpi(ext, config_cmd):
    from textwrap import dedent
    from mpidistutils import log
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
    impls = ("OPEN_MPI", "MSMPI_VER")
    tests = ["defined(%s)" % macro for macro in impls]
    tests += ["(defined(MPICH_NAME)&&(MPICH_NAME>=3))"]
    tests += ["(defined(MPICH_NAME)&&(MPICH_NAME==2))"]
    ConfigTest = dedent("""\
    #if !(%s)
    #error "Unknown MPI implementation"
    #endif
    """) % "||".join(tests)
    config = os.environ.get('MPI4PY_BUILD_CONFIGURE') or None
    if not config:
        ok = config_cmd.try_compile(ConfigTest, headers=headers)
        config = not ok
    if config:
        if not config_cmd.check_macro("HAVE_CONFIG_H"):
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
                function, arglist, headers=headers,
            )
            if not ok:
                macro = 'PyMPI_MISSING_' + function
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
    py_enable_shared = cfg_vars.get('Py_ENABLE_SHARED')
    if pyver >= (3, 8) or not py_enable_shared:
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
    #
    libdir = shlex.split(cfg_vars.get('LIBDIR', ''))
    libpl = shlex.split(cfg_vars.get('LIBPL', ''))
    if py_enable_shared:
        library_dirs += libdir
        if sys.exec_prefix != '/usr':
            runtime_dirs += libdir
    else:
        library_dirs += libdir
        library_dirs += libpl
    for var in ('LIBS', 'MODLIBS', 'SYSLIBS', 'LDLAST'):
        link_args += shlex.split(cfg_vars.get(var, ''))
    #
    exe.libraries += libraries
    exe.library_dirs += library_dirs
    exe.runtime_library_dirs += runtime_dirs
    exe.extra_link_args += link_args


def sources():
    # mpi4py.MPI
    MPI = dict(
        source='mpi4py/MPI.pyx',
        depends=[
            'mpi4py/*.pyx',
            'mpi4py/*.pxd',
            'mpi4py/MPI/*.pyx',
            'mpi4py/MPI/*.pxd',
            'mpi4py/MPI/*.pxi',
        ],
        workdir='src',
    )
    #
    return [MPI]


def extensions():
    # MPI extension module
    MPI = dict(
        name='mpi4py.MPI',
        sources=['src/mpi4py/MPI.c'],
        depends=(
            glob.glob('src/*.h') +
            glob.glob('src/lib-mpi/*.h') +
            glob.glob('src/lib-mpi/config/*.h') +
            glob.glob('src/lib-mpi/compat/*.h')
        ),
        include_dirs = ['src'],
        define_macros=[
            ('MPICH_SKIP_MPICXX', 1),
            ('OMPI_SKIP_MPICXX', 1),
        ],
        configure=configure_mpi,
    )
    #
    return [MPI]


def executables():
    # MPI-enabled Python interpreter
    pyexe = dict(
        name='python-mpi',
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

package_info = dict(
    packages = [
        'mpi4py',
        'mpi4py.futures',
        'mpi4py.util',
    ],
    package_data = {
        'mpi4py' : [
            '*.pxd',
            'MPI*.h',
            'include/mpi4py/*.h',
            'include/mpi4py/*.i',
            'include/mpi4py/*.pxi',
            'py.typed',
            '*.pyi',
            '*/*.pyi',
        ],
    },
    package_dir = {'' : 'src'},
)
if sys.version_info < (3, 7):
    del package_info['package_data']['mpi4py'][-3:]


def run_setup():
    """
    Call setuptools.setup(*args, **kwargs)
    """
    try:
        import setuptools
    except ImportError:
        setuptools = None
    from mpidistutils import setup
    from mpidistutils import Extension  as Ext
    from mpidistutils import Executable as Exe
    #
    from mpidistutils import build_src
    build_src.sources = sources()
    #
    builder_args = dict(
        ext_modules = [Ext(**ext) for ext in extensions()],
        executables = [Exe(**exe) for exe in executables()],
    )
    if setuptools:
        builder_args['zip_safe'] = False
        metadata.update(metadata_extra)
    #
    setup_args = dict(i for d in (
        metadata,
        package_info,
        builder_args,
    ) for i in d.items())
    #
    setup(**setup_args)


def run_skbuild():
    """
    Call skbuild.setup(*args, **kwargs)
    """
    from skbuild import setup
    #
    builder_args = dict(
        cmake_source_dir = 'src/mpi4py',
    )
    metadata.update(metadata_extra)
    #
    setup_args = dict(i for d in (
        metadata,
        package_info,
        builder_args,
    ) for i in d.items())
    #
    setup(**setup_args)


# --------------------------------------------------------------------


def get_backend_name(default='default'):
    return os.environ.get(
        'MPI4PY_BUILD_BACKEND', default
    ).lower().replace('_', '-')


def main():
    backend = get_backend_name()
    if backend == 'default':
        run_setup()
    elif backend in ('setuptools', 'distutils'):
        run_setup()
    elif backend in ('scikit-build', 'skbuild'):
        run_skbuild()
    else:
        sys.exit("Unknown build backend '{}'".format(backend))


if __name__ == '__main__':
    if sys.version_info < require_python:
        raise SystemExit(
            "error: requires Python version " +
            metadata_extra['python_requires']
        )
    main()


# --------------------------------------------------------------------
