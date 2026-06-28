import os
import pathlib
import re
import sys

topdir = pathlib.Path(__file__).resolve().parent.parent


def get_version(settings=None):  # noqa: ARG001
    source = topdir / "src" / "mpi4py" / "__init__.py"
    content = source.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"(.*)"', content)
    assert m is not None  # noqa: S101
    version = m.groups()[0]
    local_version = os.environ.get("MPI4PY_LOCAL_VERSION")
    if local_version:
        version = f"{version}+{local_version}"
    return version


def get_readme(settings=None):  # noqa: ARG001
    filelist = ("DESCRIPTION.rst", "CITATION.rst", "INSTALL.rst")
    template = "See `{0} <{0}>`_.\n\n"
    template += ".. include:: {0}\n"
    text = template.format(filelist[0])
    for filename in filelist:
        source = topdir / filename
        content = source.read_text(encoding="utf-8")
        includeline = template.format(filename)
        text = text.replace(includeline, content)
    return {
        "text": text,
        "content-type": "text/x-rst",
    }


def get_requires_python(settings=None):  # noqa: ARG001
    source = topdir / "pyproject.toml"
    content = source.read_text(encoding="utf-8")
    m = re.search(r"requires-python\s*=\s*\"(.*)\"", content)
    assert m is not None  # noqa: S101
    requires_python = m.groups()[0]
    return requires_python


def dynamic_metadata(field, settings=None):
    getter = globals()["get_" + field.replace("-", "_")]
    return getter(settings)


if __name__ == "__main__":
    print(dynamic_metadata(sys.argv[1]))
