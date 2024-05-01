#!/usr/bin/env python
# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""mpi4py: Python bindings for MPI."""
# ruff: noqa: C408
# ruff: noqa: D103
# ruff: noqa: S101
import os
import sys
import glob

topdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(topdir, 'conf'))

# --------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------

require_python = (3, 6)
maxknow_python = (3, 12)


def get_metadata():
    import metadata as md
    req_py = '>={}.{}'.format(*require_python)
    assert req_py == md.requires_python
    author = md.authors[0]
    readme = md.get_readme()
    return {
        # distutils
        'name'             : md.get_name(),
        'version'          : md.get_version(),
        'description'      : md.description,
        'long_description' : readme['text'],
        'classifiers'      : md.classifiers,
        'keywords'         : md.keywords,
        'license'          : md.license,
        'author'           : author['name'],
        'author_email'     : author['email'],
        # setuptools
        'project_urls': md.urls,
        'python_requires': md.requires_python,
        'long_description_content_type': readme['content-type'],
    }


# --------------------------------------------------------------------
# Extension modules
# --------------------------------------------------------------------

def sources():
    # mpi4py.MPI
    MPI = dict(
        source='src/mpi4py/MPI.pyx',
        depends=[
            'src/mpi4py/*.pyx',
            'src/mpi4py/*.pxd',
            'src/mpi4py/MPI.src/*.pyx',
            'src/mpi4py/MPI.src/*.pxi',
        ],
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
        include_dirs=['src'],
        define_macros=[],
        configure=mpidistutils.configure_mpi,
    )
    if sys.version_info[:2] > maxknow_python:
        api = '0x{:02x}{:02x}0000'.format(*maxknow_python)
        MPI['define_macros'].extend([
            ('CYTHON_LIMITED_API', api),
        ])
    if os.environ.get('CIBUILDWHEEL') == '1':
        MPI['define_macros'].extend([
            ('CIBUILDWHEEL', 1),
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
if sys.version_info < (3, 8):
    del package_info['package_data']['mpi4py'][-3:]


def run_setup():
    """Call setuptools.setup(*args, **kwargs)."""
    try:
        import setuptools
    except ImportError as exc:
        setuptools = None
        if sys.version_info >= (3, 12):
            sys.exit(exc)
    from mpidistutils import setup
    from mpidistutils import Extension  as Ext
    from mpidistutils import Executable as Exe
    #
    from mpidistutils import build_src
    build_src.sources = sources()
    #
    metadata = get_metadata()
    builder_args = dict(
        ext_modules = [Ext(**ext) for ext in extensions()],
        executables = [Exe(**exe) for exe in executables()],
    )
    if setuptools:
        builder_args['zip_safe'] = False
    else:
        metadata.pop('project_urls')
        metadata.pop('python_requires')
        metadata.pop('long_description_content_type')
    #
    setup_args = dict(i for d in (
        metadata,
        package_info,
        builder_args,
    ) for i in d.items())
    #
    setup(**setup_args)


def run_skbuild():
    """Call setuptools.setup(*args, **kwargs)."""
    from setuptools import setup
    #
    metadata = get_metadata()
    builder_args = dict(
        cmake_source_dir = '.',
    )
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
            ".".join(map(str, require_python))
        )
    main()


# --------------------------------------------------------------------
