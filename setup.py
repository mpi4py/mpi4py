#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

__doc__ = \
"""
Python bindings for MPI
"""

import os
import sys
import glob

topdir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(topdir, 'conf'))

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

def get_name():
    return 'mpi4py'

def get_version():
    import getversion
    try:
        return get_version.result
    except AttributeError:
        pass
    version = getversion.version()
    get_version.result = version
    return version

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
    version = get_version().partition('+')[0]
    if '.dev' in version:
        path = 'tarball'
        archive = 'master'
    else:
        path = 'releases/download/{0}'.format(version)
        archive = 'mpi4py-{0}.tar.gz'.format(version)
    return github(path, archive)

def documentation_url():
    version = get_version().partition('+')[0]
    language = 'en'
    location = 'latest' if '.dev' in version else version
    return readthedocs(language, location, '')

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
    'name'             : get_name(),
    'version'          : get_version(),
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
maxknow_python = (3, 11)

metadata_extra = {
    'project_urls': {
        "Source Code"   : github(),
        "Bug Tracker"   : github('issues'),
        "Discussions"   : github('discussions'),
        "Documentation" : documentation_url(),
    },
    'python_requires': '>=' + '.'.join(map(str, require_python)),
    'long_description_content_type': 'text/x-rst',
}

# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

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
    import mpidistutils
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
        configure=mpidistutils.configure_mpi,
    )
    if sys.version_info[:2] > maxknow_python:
        MPI['define_macros'].extend([
            ('CYTHON_FAST_PYCALL', 0),
            ('CYTHON_FAST_THREAD_STATE', 0),
            ('CYTHON_USE_DICT_VERSIONS', 0),
            ('CYTHON_USE_PYLONG_INTERNALS', 0),
            ('CYTHON_USE_PYLIST_INTERNALS', 0),
            ('CYTHON_USE_UNICODE_INTERNALS', 0),
        ])
    #
    return [MPI]


def executables():
    import mpidistutils
    # MPI-enabled Python interpreter
    pyexe = dict(
        name='python-mpi',
        optional=True,
        package='mpi4py',
        dest_dir='bin',
        sources=['src/python.c'],
        configure=mpidistutils.configure_pyexe,
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
    Call setuptools.setup(*args, **kwargs)
    """
    from setuptools import setup
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


def main():
    try:
        import builder
        name = builder.get_build_backend_name()
    except RuntimeError as exc:
        sys.exit(exc)

    if name == 'setuptools':
        run_setup()
    if name == 'skbuild':
        run_skbuild()


if __name__ == '__main__':
    if sys.version_info < require_python:
        raise SystemExit(
            "error: requires Python version " +
            metadata_extra['python_requires']
        )
    main()


# --------------------------------------------------------------------
