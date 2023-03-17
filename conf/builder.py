import contextlib
import importlib
import os
import shutil

# ---


def setup_env_mpicc():
    mpicc = shutil.which('mpicc')
    mpicc = os.environ.get('MPICC', mpicc)
    mpicc = os.environ.get('MPI4PY_BUILD_MPICC', mpicc)
    if not mpicc:
        return
    if ' ' in mpicc:
        mpicc = f'"{mpicc}"'
    if 'CC' not in os.environ:
        os.environ['CC'] =  mpicc


# ---

def get_backend_name(default='default'):
    name = os.environ.get(
        'MPI4PY_BUILD_BACKEND', default,
    ).lower().replace('_', '-')
    if name in ('default', ''):
        return 'setuptools'
    if name in ('setuptools', 'setup'):
        return 'setuptools'
    if name in ('scikit-build', 'skbuild', 'cmake'):
        return 'scikit-build'
    if name in ('meson-python', 'mesonpy', 'meson'):
        return 'meson-python'
    raise RuntimeError(f"Unknown build backend {name!r}")


def read_build_requires(package):
    confdir = os.path.dirname(__file__)
    basename = f'requirements-build-{package}.txt'
    with open(os.path.join(confdir, basename)) as f:
        return [req for req in map(str.strip, f) if req]


def get_requires_for_build(dist):
    name = get_backend_name()
    requires = []
    if dist == 'wheel':
        if name == 'scikit-build':
            requires += read_build_requires('skbuild')
        if name == 'meson-python':
            requires += read_build_requires('mesonpy')
    if dist in ('wheel', 'editable'):
        requires += read_build_requires('cython')
    return requires


@contextlib.contextmanager
def build_backend(name='default'):
    name_saved = os.environ.get('MPI4PY_BUILD_BACKEND')
    os.environ['MPI4PY_BUILD_BACKEND'] = name
    try:
        name = get_backend_name()
        if name == 'setuptools':
            yield importlib.import_module('setuptools.build_meta')
        if name == 'scikit-build':
            yield importlib.import_module('setuptools.build_meta')
        if name == 'meson-python':
            setup_env_mpicc()
            yield importlib.import_module('mesonpy')
    finally:
        if name_saved is None:
            del os.environ['MPI4PY_BUILD_BACKEND']
        else:
            os.environ['MPI4PY_BUILD_BACKEND'] = name_saved


# ---


def get_requires_for_build_sdist(config_settings=None):
    with build_backend() as backend:
        requires = backend.get_requires_for_build_sdist(config_settings)
    requires += get_requires_for_build('sdist')
    return requires


def build_sdist(
    sdist_directory,
    config_settings=None,
):
    with build_backend() as backend:
        return backend.build_sdist(
            sdist_directory,
            config_settings,
        )


# ---


def get_requires_for_build_wheel(config_settings=None):
    with build_backend() as backend:
        requires = backend.get_requires_for_build_wheel(config_settings)
    requires += get_requires_for_build('wheel')
    return requires


def prepare_metadata_for_build_wheel(
    metadata_directory,
    config_settings=None,
):
    name = get_backend_name()
    with build_backend(name) as backend:
        return backend.prepare_metadata_for_build_wheel(
            metadata_directory,
            config_settings,
        )


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    name = get_backend_name()
    with build_backend(name) as backend:
        return backend.build_wheel(
            wheel_directory,
            config_settings,
            metadata_directory,
        )


# ---


def get_requires_for_build_editable(config_settings=None):
    with build_backend() as backend:
        requires = backend.get_requires_for_build_editable(config_settings)
    requires += get_requires_for_build('editable')
    return requires


def prepare_metadata_for_build_editable(
    metadata_directory,
    config_settings=None,
):
    name = 'setuptools'  # TODO: support scikit-build
    with build_backend(name) as backend:
        return backend.prepare_metadata_for_build_editable(
            metadata_directory,
            config_settings,
        )


def build_editable(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    name = 'setuptools'  # TODO: support scikit-build
    with build_backend(name) as backend:
        return backend.build_editable(
            wheel_directory,
            config_settings,
            metadata_directory,
        )

# ---

if get_backend_name() == 'setuptools':
    try:
        import setuptools.build_meta as st_bm
    except ImportError:
        st_bm = None
    if not hasattr(st_bm, 'get_requires_for_build_editable'):
        del get_requires_for_build_editable
    if not hasattr(st_bm, 'prepare_metadata_for_build_editable'):
        del prepare_metadata_for_build_editable
    if not hasattr(st_bm, 'build_editable'):
        del build_editable
    del st_bm

if get_backend_name() == 'meson-python':
    del prepare_metadata_for_build_wheel
    del get_requires_for_build_editable
    del prepare_metadata_for_build_editable
    del build_editable

# ---
