import contextlib
import importlib
import os
import shutil
import sys

# ---

BACKENDS = {
    'setuptools': 'setuptools.build_meta',
    'skbuild': 'scikit_build_core.setuptools.build_meta',
    'mesonpy': 'mesonpy',
}


def get_build_backend_name(name=None):
    if name is None:
        name = os.environ.get('MPI4PY_BUILD_BACKEND', '')
        name = name.lower().replace('_', '-')
    if name in ('default', ''):
        for name, module_name in BACKENDS.items():
            if name != 'setuptools':
                if module_name in sys.modules:
                    return name
        return 'setuptools'
    if name in ('setuptools', 'setup'):
        return 'setuptools'
    if name in ('scikit-build-core', 'scikit-build', 'skbuild', 'cmake'):
        return 'skbuild'
    if name in ('meson-python', 'mesonpy', 'meson'):
        return 'mesonpy'
    raise RuntimeError(f"Unknown build backend {name!r}")


def build_backend(name=None):
    name = get_build_backend_name(name)
    return importlib.import_module(BACKENDS[name])


def read_build_requires(name):
    confdir = os.path.dirname(__file__)
    basename = f'requirements-build-{name}.txt'
    filename = os.path.join(confdir, basename)
    with open(filename, encoding='utf-8') as f:
        return [req for req in map(str.strip, f) if req]


def get_backend_requires_fast(backend, dist, config_settings=None):
    if backend is None or isinstance(backend, str):
        try:
            backend = build_backend(backend)
        except ImportError:
            return None
    requires = []
    get_requires = getattr(backend, f'get_requires_for_build_{dist}', None)
    if get_requires is not None:
        requires += get_requires(config_settings)
    return requires


def get_backend_requires_hook(name, dist, config_settings=None):
    from build.env import IsolatedEnvBuilder
    try:
        from pyproject_hooks import BuildBackendHookCaller
    except ImportError:
        from pep517.wrappers import Pep517HookCaller as BuildBackendHookCaller

    @contextlib.contextmanager
    def environment(scripts_dir):
        os_path = os.environ.get('PATH')
        paths = os_path.split(os.pathsep) if os_path else []
        while scripts_dir in paths:
            paths.remove(scripts_dir)
        paths.insert(0, scripts_dir)
        os.environ['PATH'] = os.pathsep.join(paths)
        build_backend = os.environ.pop('PEP517_BUILD_BACKEND', None)
        backend_path = os.environ.pop('PEP517_BACKEND_PATH', None)
        try:
            yield None
        finally:
            if os_path is not None:
                os.environ['PATH'] = os_path
            if build_backend is not None:
                os.environ['PEP517_BUILD_BACKEND'] = build_backend
            if backend_path is not None:
                os.environ['PEP517_BACKEND_PATH'] = backend_path

    requires = read_build_requires(name)
    with IsolatedEnvBuilder() as env:
        with environment(env.scripts_dir):
            env.install(requires)
            hook = BuildBackendHookCaller(
                source_dir=os.getcwd(),
                build_backend=BACKENDS[name],
                python_executable=env.executable,
            )
            requires += get_backend_requires_fast(hook, dist, config_settings)
    return requires


def get_requires_for_build(dist, config_settings=None):
    name = get_build_backend_name()
    requires = get_backend_requires_fast(name, dist, config_settings)
    if requires is None:
        requires = get_backend_requires_hook(name, dist, config_settings)
    if dist in ('wheel', 'editable'):
        requires += read_build_requires('cython')
    return requires


# ---


def get_requires_for_build_sdist(config_settings=None):
    return get_requires_for_build('sdist', config_settings)


def build_sdist(
    sdist_directory,
    config_settings=None,
):
    return build_backend().build_sdist(
        sdist_directory,
        config_settings,
    )


# ---


def get_requires_for_build_wheel(config_settings=None):
    return get_requires_for_build('wheel', config_settings)


def prepare_metadata_for_build_wheel(
    metadata_directory,
    config_settings=None,
):
    return build_backend().prepare_metadata_for_build_wheel(
        metadata_directory,
        config_settings,
    )


def build_wheel(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    return build_backend().build_wheel(
        wheel_directory,
        config_settings,
        metadata_directory,
    )


# ---


def get_requires_for_build_editable(config_settings=None):
    return get_requires_for_build('editable', config_settings)


def prepare_metadata_for_build_editable(
    metadata_directory,
    config_settings=None,
):
    return build_backend().prepare_metadata_for_build_editable(
        metadata_directory,
        config_settings,
    )


def build_editable(
    wheel_directory,
    config_settings=None,
    metadata_directory=None,
):
    return build_backend().build_editable(
        wheel_directory,
        config_settings,
        metadata_directory,
    )

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
        os.environ['CC'] = mpicc


if get_build_backend_name() == 'setuptools':
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

if get_build_backend_name() == 'skbuild':
    del get_requires_for_build_editable
    del prepare_metadata_for_build_editable
    del build_editable

if get_build_backend_name() == 'mesonpy':
    setup_env_mpicc()
    del prepare_metadata_for_build_wheel
    del get_requires_for_build_editable
    del prepare_metadata_for_build_editable
    del build_editable

# ---
