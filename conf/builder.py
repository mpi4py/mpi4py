import os
import sys
import shutil
import contextlib
import setuptools.build_meta as _st_bm

CYTHON = 'cython >= 0.27'
SKBUILD = 'scikit-build >= 0.13'
CMAKE = 'cmake >= 3.12'
NINJA = 'ninja'


def get_backend_name(default='default'):
    return os.environ.get(
        'MPI4PY_BUILD_BACKEND', default
    ).lower().replace('_', '-')


@contextlib.contextmanager
def set_build_backend(backend='default'):
    backend_saved = os.environ.get('MPI4PY_BUILD_BACKEND')
    try:
        os.environ['MPI4PY_BUILD_BACKEND'] = backend
        yield
    finally:
        if backend_saved is None:
            del os.environ['MPI4PY_BUILD_BACKEND']
        else:
            os.environ['MPI4PY_BUILD_BACKEND'] = backend_saved


def get_requires_for_build_wheel(config_settings=None):
    backend = get_backend_name()
    use_skbuild = backend in ('scikit-build', 'skbuild')
    with set_build_backend():
        requires = _st_bm.get_requires_for_build_wheel(config_settings)
    if use_skbuild:
        requires.append(CYTHON)
        requires.append(SKBUILD)
        requires.append(CMAKE)
        requires.append(NINJA)
    return requires


def get_requires_for_build_sdist(config_settings=None):
    with set_build_backend():
        requires = _st_bm.get_requires_for_build_sdist(config_settings)
    requires.append(CYTHON)
    return requires


def prepare_metadata_for_build_wheel(
    metadata_directory,
    config_settings=None,
):
    with set_build_backend():
        return _st_bm.prepare_metadata_for_build_wheel(
            metadata_directory,
            config_settings,
        )


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    backend = get_backend_name()
    with set_build_backend(backend):
        return _st_bm.build_wheel(
            wheel_directory,
            config_settings,
            metadata_directory,
        )


def build_sdist(
    sdist_directory,
    config_settings=None,
):
    with set_build_backend():
        return _st_bm.build_sdist(
            sdist_directory,
            config_settings,
        )
