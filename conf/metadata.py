import re
import os
import sys


def get_name(settings=None):  # noqa: ARG001
    name = "mpi4py"
    suffix = os.environ.get("MPI4PY_DIST_SUFFIX")
    if suffix:
        name = "{name}-{suffix}".format(**vars())
    return name


def get_version(settings=None):  # noqa: ARG001
    confdir = os.path.dirname(os.path.abspath(__file__))
    topdir = os.path.dirname(confdir)
    srcdir = os.path.join(topdir, "src")
    source = os.path.join(srcdir, "mpi4py", "__init__.py")
    with open(source, encoding="utf-8") as f:
        m = re.search(r"__version__\s*=\s*'(.*)'", f.read())
    version = m.groups()[0]
    local_version = os.environ.get("MPI4PY_LOCAL_VERSION")
    if local_version:
        version = "{version}+{local_version}".format(**vars())
    return version


def get_readme(settings=None):  # noqa: ARG001
    confdir = os.path.dirname(__file__)
    topdir = os.path.dirname(confdir)
    filelist = ("DESCRIPTION.rst", "CITATION.rst", "INSTALL.rst")
    template = "See `{0} <{0}>`_.\n\n"
    template += ".. include:: {0}\n"
    text = template.format(filelist[0])
    for filename in filelist:
        source = os.path.join(topdir, filename)
        with open(source, encoding="utf-8") as f:
            includeline = template.format(filename)
            text = text.replace(includeline, f.read())
    return {
        "text": text,
        "content-type": "text/x-rst",
    }


description = "Python bindings for MPI"
requires_python = ">=3.6"
license = "BSD-3-Clause"
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
    "License :: OSI Approved :: BSD License",
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
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Distributed Computing",
    "Typing :: Typed",
]
urls = {
    "Homepage":      "https://mpi4py.github.io",
    "Documentation": "https://mpi4py.readthedocs.io/en/stable/",
    "Source":        "https://github.com/mpi4py/mpi4py",
    "Issues":        "https://github.com/mpi4py/mpi4py/issues",
    "Discussions":   "https://github.com/mpi4py/mpi4py/discussions",
    "Downloads":     "https://github.com/mpi4py/mpi4py/releases",
}


def dynamic_metadata(field, settings=None):
    getter = globals().get("get_" + field)
    if getter:
        return getter(settings)
    return globals()[field.replace(".", "_")]


if __name__ == "__main__":
    print(dynamic_metadata(sys.argv[1]))
