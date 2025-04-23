import contextlib
import importlib
import os
import pathlib
import shutil
import sys

# ---

BACKENDS = {
    "setuptools": "setuptools.build_meta",
    "skbuild": "scikit_build_core.setuptools.build_meta",
    "mesonpy": "mesonpy",
}


def get_build_backend_name(name=None):
    if name is None:
        name = os.environ.get("MPI4PY_BUILD_BACKEND", "")
        name = name.lower().replace("_", "-")
    if name in ("default", ""):
        for name, module_name in BACKENDS.items():
            if name != "setuptools":
                if module_name in sys.modules:
                    return name
        return "setuptools"
    if name in ("setuptools", "setup"):
        return "setuptools"
    if name in ("scikit-build-core", "scikit-build", "skbuild", "cmake"):
        return "skbuild"
    if name in ("meson-python", "mesonpy", "meson"):
        return "mesonpy"
    raise RuntimeError(f"Unknown build backend {name!r}")


def build_backend(name=None):
    name = get_build_backend_name(name)
    return importlib.import_module(BACKENDS[name])


def read_build_requires(name):
    confdir = pathlib.Path(__file__).parent
    basename = f"requirements-build-{name}.txt"
    filename = confdir / basename
    with filename.open(encoding="utf-8") as f:
        return [req for req in map(str.strip, f) if req]


def get_backend_requires_fast(backend, dist, config_settings=None):
    if backend is None or isinstance(backend, str):
        try:
            backend = build_backend(backend)
        except ImportError:
            return None
    requires = []
    get_requires = getattr(backend, f"get_requires_for_build_{dist}", None)
    if get_requires is not None:
        requires += get_requires(config_settings)
    return requires


def get_backend_requires_hook(name, dist, config_settings=None):
    try:
        from pyproject_hooks import BuildBackendHookCaller
    except ImportError:
        from pep517.wrappers import Pep517HookCaller as BuildBackendHookCaller
    try:
        from build.env import DefaultIsolatedEnv
    except ImportError:
        from build.env import IsolatedEnvBuilder

        class DefaultIsolatedEnv(IsolatedEnvBuilder):
            def __enter__(self):
                env = super().__enter__()
                env.python_executable = env.executable

                def make_extra_environ():
                    path = os.environ.get("PATH")
                    return {
                        "PATH": os.pathsep.join([env.scripts_dir, path])
                        if path is not None
                        else env.scripts_dir,
                    }

                env.make_extra_environ = make_extra_environ
                return env

    @contextlib.contextmanager
    def environment(path):
        environ_prev = [("PATH", os.environ["PATH"])]
        for prefix in ("_PYPROJECT_HOOKS", "PEP517"):
            for suffix in ("BUILD_BACKEND", "BACKEND_PATH"):
                key = f"{prefix}_{suffix}"
                if key in os.environ:
                    val = os.environ.pop(key)
                    environ_prev.append((key, val))
        os.environ["PATH"] = path
        try:
            yield None
        finally:
            os.environ.update(environ_prev)

    requires = read_build_requires(name)
    with DefaultIsolatedEnv() as env:
        path = env.make_extra_environ()["PATH"]
        python_executable = env.python_executable
        with environment(path):
            env.install(requires)
            hook = BuildBackendHookCaller(
                source_dir=pathlib.Path.cwd(),
                build_backend=BACKENDS[name],
                python_executable=python_executable,
            )
            requires += get_backend_requires_fast(hook, dist, config_settings)
    return requires


def get_requires_for_build(dist, config_settings=None):
    name = get_build_backend_name()
    requires = get_backend_requires_fast(name, dist, config_settings)
    if requires is None:
        requires = get_backend_requires_hook(name, dist, config_settings)
    if dist in ("wheel", "editable"):
        requires += read_build_requires("cython")
    return requires


# ---


def get_requires_for_build_sdist(config_settings=None):
    return get_requires_for_build("sdist", config_settings)


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
    return get_requires_for_build("wheel", config_settings)


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
    return get_requires_for_build("editable", config_settings)


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
    mpicc = shutil.which("mpicc")
    mpicc = os.environ.get("MPICC", mpicc)
    mpicc = os.environ.get("MPI4PY_BUILD_MPICC", mpicc)
    if not mpicc:
        return
    if " " in mpicc:
        mpicc = f'"{mpicc}"'
    if "CC" not in os.environ:
        os.environ["CC"] = mpicc


if get_build_backend_name() == "setuptools":
    try:
        import setuptools.build_meta as st_bm
    except ImportError:
        st_bm = None
    if not hasattr(st_bm, "get_requires_for_build_editable"):
        del get_requires_for_build_editable
    if not hasattr(st_bm, "prepare_metadata_for_build_editable"):
        del prepare_metadata_for_build_editable
    if not hasattr(st_bm, "build_editable"):
        del build_editable
    del st_bm

if get_build_backend_name() == "mesonpy":
    setup_env_mpicc()
    del prepare_metadata_for_build_wheel
    del prepare_metadata_for_build_editable

# ---
