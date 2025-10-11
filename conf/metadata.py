import os
import pathlib
import re
import sys


def get_name(settings=None):  # noqa: ARG001
    name = "mpi4py"
    suffix = os.environ.get("MPI4PY_DIST_SUFFIX")
    if suffix:
        name = f"{name}-{suffix}"
    return name


def get_version(settings=None):  # noqa: ARG001
    topdir = pathlib.Path(__file__).resolve().parent.parent
    source = topdir / "src" / "mpi4py" / "__init__.py"
    content = source.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"(.*)"', content)
    version = m.groups()[0]
    local_version = os.environ.get("MPI4PY_LOCAL_VERSION")
    if local_version:
        version = f"{version}+{local_version}"
    return version


def get_readme(settings=None):  # noqa: ARG001
    topdir = pathlib.Path(__file__).resolve().parent.parent
    filelist = ("DESCRIPTION.rst", "CITATION.rst", "INSTALL.rst")
    template = "See `{0} <{0}>`_.\n\n"
    template += ".. include:: {0}\n"
    text = template.format(filelist[0])
    for filename in filelist:
        source = topdir / filename
        with source.open(encoding="utf-8") as f:
            includeline = template.format(filename)
            text = text.replace(includeline, f.read())
    return {
        "text": text,
        "content-type": "text/x-rst",
    }


description = "Python bindings for MPI"
requires_python = ">=3.10"
license = "BSD-3-Clause"  # noqa: A001
authors = [
    {"name": "Lisandro Dalcin", "email": "dalcinl@gmail.com"},
]
keywords = [
    "scientific computing",
    "parallel computing",
    "message passing interface",
    "MPI",
]
classifiers = [
    "Development Status :: 6 - Mature",
    "Environment :: GPU",
    "Environment :: GPU :: NVIDIA CUDA",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Operating System :: MacOS",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: POSIX :: BSD",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Unix",
    "Programming Language :: C",
    "Programming Language :: Cython",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Distributed Computing",
    "Typing :: Typed",
]
urls = {
    "Homepage":      "https://mpi4py.github.io/mpi4py/",
    "Documentation": "https://mpi4py.readthedocs.io/en/stable/",
    "Source":        "https://github.com/mpi4py/mpi4py",
    "Issues":        "https://github.com/mpi4py/mpi4py/issues",
    "Discussions":   "https://github.com/mpi4py/mpi4py/discussions",
    "Downloads":     "https://github.com/mpi4py/mpi4py/releases",
}  # fmt: skip


def dynamic_metadata(field, settings=None):
    getter = globals().get("get_" + field)
    if getter:
        return getter(settings)
    return globals()[field.replace(".", "_")]


if __name__ == "__main__":
    print(dynamic_metadata(sys.argv[1]))
