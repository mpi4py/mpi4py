import os
import sys
import shutil
import contextlib
import setuptools.build_meta as _st_bm

CYTHON = "cython >= 0.28"
SKBUILD = "scikit-build >= 0.13"
CMAKE = "cmake >= 3.12"
NINJA = "ninja; platform_system!='Windows'"


def get_backend_name(default='default'):
    return os.environ.get(
        'MPI4PY_BUILD_BACKEND', default
    ).lower().replace('_', '-')


def get_build_requires():
    name = get_backend_name()
    use_skbuild = name in ('scikit-build', 'skbuild')
    requires = []
    requires.append(CYTHON)
    if use_skbuild:
        requires.append(SKBUILD)
        requires.append(CMAKE)
        requires.append(NINJA)
    return requires


@contextlib.contextmanager
def set_build_backend(name='default'):
    name_saved = os.environ.get('MPI4PY_BUILD_BACKEND')
    try:
        os.environ['MPI4PY_BUILD_BACKEND'] = name
        yield _st_bm
    finally:
        if name_saved is None:
            del os.environ['MPI4PY_BUILD_BACKEND']
        else:
            os.environ['MPI4PY_BUILD_BACKEND'] = name_saved


def get_requires_for_build_sdist(config_settings=None):
    with set_build_backend() as backend:
        requires = backend.get_requires_for_build_sdist(config_settings)
    return requires


def get_requires_for_build_wheel(config_settings=None):
    with set_build_backend() as backend:
        requires = backend.get_requires_for_build_wheel(config_settings)
    requires += get_build_requires()
    return requires


def get_requires_for_build_editable(config_settings=None):
    with set_build_backend() as backend:
        requires = backend.get_requires_for_build_editable(config_settings)
    requires += get_build_requires()
    return requires


def prepare_metadata_for_build_wheel(
    metadata_directory,
    config_settings=None,
):
    with set_build_backend() as backend:
        return backend.prepare_metadata_for_build_wheel(
            metadata_directory,
            config_settings,
        )


def prepare_metadata_for_build_editable(
    metadata_directory,
    config_settings=None,
):
    with set_build_backend() as backend:
        return backend.prepare_metadata_for_build_editable(
            metadata_directory,
            config_settings,
        )


def build_sdist(
    sdist_directory,
    config_settings=None,
):
    with set_build_backend() as backend:
        return backend.build_sdist(
            sdist_directory,
            config_settings,
        )


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    name = get_backend_name()
    with set_build_backend(name) as backend:
        return backend.build_wheel(
            wheel_directory,
            config_settings,
            metadata_directory,
        )


def build_editable(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    name = 'default'  # TODO: support scikit-build
    with set_build_backend(name) as backend:
        return backend.build_editable(
            wheel_directory,
            config_settings,
            metadata_directory,
        )


if not hasattr(_st_bm, 'get_requires_for_build_editable'):
    del get_requires_for_build_editable

if not hasattr(_st_bm, 'prepare_metadata_for_build_editable'):
    del prepare_metadata_for_build_editable

if not hasattr(_st_bm, 'build_editable'):
    del build_editable
