"""https://github.com/scientific-python/spin"""  # noqa: D400

import os
import pathlib
import shlex
import shutil
import sys

import click
from spin.cmds.util import run

PYTHON = shlex.split(os.environ.get("PYTHON", sys.executable))
MPIEXEC = shlex.split(os.environ.get("MPIEXEC", "mpiexec"))
SHELL = shlex.split(os.environ.get("SHELL", "sh"))


@click.command()
@click.option("-c", "--clean", is_flag=True, help="Clean build directory.")
@click.option("-f", "--force", is_flag=True, help="Force build everything.")
@click.option("-q", "--quiet", is_flag=True, help="Run quietly.")
def build(clean, force, quiet):
    """🔧 Build in-place."""
    opt_force = ["--force"] if force else []
    opt_quiet = ["--quiet"] if quiet else []
    if clean:
        run([*PYTHON, "setup.py", *opt_quiet, "clean", "--all"])
    run([*PYTHON, "setup.py", *opt_quiet, "build", *opt_force, "--inplace"])


@click.command()
@click.option("-n", default=2, help="Number of MPI processes")
@click.option("-s", "--singleton", is_flag=True, help="Singleton mode.")
@click.pass_context
def check(ctx, n, singleton):
    """🔧 Check in-place."""
    ctx.invoke(build, quiet=True)
    launcher = [] if singleton else [*MPIEXEC, "-n", f"{n}"]
    run([*PYTHON, "-m", "mpi4py", "--prefix"])
    run([*PYTHON, "-m", "mpi4py", "--mpi-library"])
    run([*launcher, *PYTHON, "-m", "mpi4py.bench", "ringtest"])


@click.command()
@click.option("-n", default=1, help="Number of MPI processes")
@click.option("-s", "--singleton", is_flag=True, help="Singleton mode.")
@click.argument("test_args", nargs=-1)
@click.pass_context
def test(ctx, n, singleton, test_args):
    """🔧 Test in-place."""
    ctx.invoke(build, quiet=True)
    launcher = [] if singleton else [*MPIEXEC, "-n", f"{n}"]
    run([*launcher, *PYTHON, "test/main.py", "--inplace", *test_args])


def _get_topdir():
    script = pathlib.Path(__file__).resolve()
    return script.parent.parent


def _get_site_packages():
    return _get_topdir() / "src"


def _set_pythonpath(path, quiet=False):
    pythonpath = os.environ.get("PYTHONPATH")
    if pythonpath is not None:
        pythonpath = f"{path}{os.pathsep}{pythonpath}"
    else:
        pythonpath = f"{path}"
    os.environ["PYTHONPATH"] = pythonpath
    if not quiet:
        click.secho(
            f'$ export PYTHONPATH="{pythonpath}"',
            bold=True,
            fg="bright_blue",
        )
    return path


def _setup_environment(ctx, quiet=False):
    path = _get_site_packages()
    ctx.invoke(build, quiet=True)
    _set_pythonpath(path, quiet=quiet)


def _run_check_commands(*commands):
    for cmd, *args in commands:
        if shutil.which(cmd) is not None:
            run([cmd, *args])
        else:
            click.secho(
                f"{cmd}: command not found...",
                bold=True,
                fg="bright_red",
            )


@click.command()
@click.pass_context
def lint(ctx):
    """🔦 Lint-check sources with linters."""
    _setup_environment(ctx)
    _run_check_commands(
        ["ruff", "check", "--quiet"],
        ["ruff", "format", "--quiet", "--diff"],
        ["flake8", "docs", "src"],
        ["pylint", "mpi4py"],
        ["cython-lint", "."],
        ["codespell"],
        ["yamllint", "."],
    )


@click.command()
@click.pass_context
def type(ctx):  # noqa: A001
    """🦆 Type-check sources with mypy."""
    _setup_environment(ctx)
    _run_check_commands(
        ["stubtest", "mpi4py"],
        ["mypy", "-p", "mpi4py"],
    )


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("shell_args", nargs=-1)
@click.pass_context
def shell(ctx, shell_args):
    """💻 Launch shell with PYTHONPATH set."""
    _setup_environment(ctx)
    run([*SHELL, *shell_args], replace=True)


@click.command(context_settings={"ignore_unknown_options": True})
@click.argument("ipython_args", nargs=-1)
@click.pass_context
def ipython(ctx, ipython_args):
    """🐍 Launch ipython with PYTHONPATH set."""
    _setup_environment(ctx)
    ipython = [*PYTHON, "-m", "IPython"]
    run([*ipython, *ipython_args], replace=True)


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("-n", default=1, help="Number of MPI processes")
@click.argument("mpiexec_args", nargs=-1)
@click.pass_context
def mpiexec(ctx, n, mpiexec_args):
    """🏁 Run mpiexec with PYTHONPATH set."""
    _setup_environment(ctx)
    run([*MPIEXEC, "-n", f"{n}", *mpiexec_args], replace=True)


@click.command(context_settings={"ignore_unknown_options": True})
@click.option("-n", default=1, help="Number of MPI processes")
@click.argument("mpi4py_args", nargs=-1)
@click.pass_context
def mpi4py(ctx, n, mpi4py_args):
    """🏁 Run mpi4py with PYTHONPATH set."""
    _setup_environment(ctx)
    mpi4py = [*MPIEXEC, "-n", f"{n}", *PYTHON, "-m", "mpi4py"]
    mpi4py_args = mpi4py_args or ["--help"]
    run([*mpi4py, *mpi4py_args], replace=True)


@click.command()
@click.option("-e", "--editable", is_flag=True, help="Editable mode.")
@click.option("-q", "--quiet", is_flag=True, help="Run quietly.")
@click.argument("pip_args", nargs=-1)
def install(editable, quiet, pip_args):
    """🔧 Install package."""
    pip = [*PYTHON, "-m", "pip"]
    pip_args = [*pip_args]
    if quiet:
        pip_args.append("--quiet")
    if editable:
        pip_args.append("--editable")
    run([*pip, "install", *pip_args, "."])


@click.command()
@click.option("-q", "--quiet", is_flag=True, help="Run quietly.")
@click.argument("pip_args", nargs=-1)
@click.pass_context
def editable(ctx, quiet, pip_args):  # noqa: ARG001
    """🔧 Install package in editable mode."""
    ctx.forward(install, editable=True)


@click.command()
def sdist():
    """📦 Build sdist."""
    run([*PYTHON, "-m", "build", ".", "--sdist"])


@click.command()
def wheel():
    """📦 Build wheel."""
    run([*PYTHON, "-m", "build", ".", "--wheel"])


@click.command()
@click.option("-b", "--builder", default="html", help="Builder to use.")
@click.option("-f", "--force", is_flag=True, help="Ignore cached environment.")
@click.option("-j", "--jobs", default="auto", help="Build in parallel.")
@click.option("-q", "--quiet", is_flag=True, help="Run quietly.")
@click.pass_context
def docs(ctx, builder="html", force=False, jobs="auto", quiet=False):
    """📖 Build Sphinx documentation."""
    sphinx = [*PYTHON, "-m", "sphinx.cmd.build"]
    srcdir = "docs/source"
    outdir = "build"
    options = []
    if quiet:
        options.append("-q")
    if force:
        options.append("-E")
    options.append("-W")
    options.extend(["--jobs", jobs])
    _setup_environment(ctx)
    run([*sphinx, "-M", builder, srcdir, outdir, *options])


@click.command()
@click.pass_context
def browse(ctx):
    """🌐 Browse Sphinx documentation."""
    ctx.invoke(docs, quiet=True)
    browser = [*PYTHON, "-m", "webbrowser", "-n"]
    url = pathlib.Path() / "build" / "html" / "index.html"
    run([*browser, str(url)])
