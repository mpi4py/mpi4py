# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import datetime
import importlib
import os
import pathlib
import re
import sys
import types
import typing

sys.path.insert(0, os.fspath(pathlib.Path.cwd()))
_today = datetime.datetime.now()


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

package = "mpi4py"


def pkg_version():
    topdir = pathlib.Path(__file__).resolve().parent.parent.parent
    source = topdir / "src" / "mpi4py" / "__init__.py"
    content = source.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"(.*)"', content)
    return m.groups()[0]


project = "MPI for Python"
author = "Lisandro Dalcin"
copyright = f"{_today.year}, {author}"  # noqa: A001

release = pkg_version()
version = release.rsplit(".", 1)[0]


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

needs_sphinx = "5.0.0"

default_role = "any"

nitpicky = True
nitpick_ignore = [
    ("c:func", r"atexit"),
    ("c:func", r"dlopen"),
    ("c:func", r"dlsym"),
    ("py:mod", r"__worker__"),
]
nitpick_ignore_regex = [
    (r"c:.*", r"MPI_.*"),
    (r"envvar", r"(LD_LIBRARY_)?PATH"),
    (r"envvar", r"(MPICH|OMPI|MPIEXEC)_.*"),
]

toc_object_entries = False
toc_object_entries_show_parents = "hide"
# python_use_unqualified_type_names = True

autodoc_default_options = {
    "exclude-members": "__new__,__init__",
}
autodoc_class_signature = "separated"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_mock_imports = []
autodoc_type_aliases = {}

autosummary_context = {
    "synopsis": {},
    "autotype": {},
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "dlpack": ("https://dmlc.github.io/dlpack/latest/", None),
    "numba": ("https://numba.readthedocs.io/en/stable/", None),
}

napoleon_preprocess_types = True

try:
    import sphinx_rtd_theme
except ImportError:
    sphinx_rtd_theme = None
else:
    if "sphinx_rtd_theme" not in extensions:
        extensions.append("sphinx_rtd_theme")

try:
    import sphinx_copybutton
except ImportError:
    sphinx_copybutton = None
else:
    if "sphinx_copybutton" not in extensions:
        extensions.append("sphinx_copybutton")

copybutton_exclude = ".linenos, .gp, .go"
copybutton_prompt_text = r"\$ |>>> |\.\.\. "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"

extensions.append("sphinx.ext.coverage")
coverage_ignore_modules = [r"mpi4py\.(bench|run)"]
coverage_ignore_classes = [r"Rc", r"memory"]


def _setup_numpy_typing():
    try:
        import numpy as np
    except ImportError:
        from typing import Generic, TypeVar

        np = type(sys)("numpy")
        sys.modules[np.__name__] = np
        np.dtype = types.new_class("dtype", (Generic[TypeVar("T")],))
        np.dtype.__module__ = np.__name__

    try:
        import numpy.typing as npt
    except ImportError:
        npt = type(sys)("numpy.typing")
        np.typing = npt
        sys.modules[npt.__name__] = npt
        npt.__all__ = []
        for attr in ["ArrayLike", "DTypeLike"]:
            setattr(npt, attr, typing.Any)
            npt.__all__.append(attr)


def _patch_domain_python():
    try:
        from numpy.typing import __all__ as numpy_types
    except ImportError:
        numpy_types = []
    try:
        from mpi4py.typing import __all__ as mpi4py_types
    except ImportError:
        mpi4py_types = []

    numpy_types = set(numpy_types)
    mpi4py_types = set(mpi4py_types)
    for name in numpy_types:
        autodoc_type_aliases[name] = f"~numpy.typing.{name}"
    for name in mpi4py_types:
        autodoc_type_aliases[name] = f"~mpi4py.typing.{name}"

    from sphinx.domains.python import PythonDomain
    from sphinx.util.inspect import TypeAliasForwardRef

    PythonDomain.object_types["data"].roles += ("class",)
    TypeAliasForwardRef.__repr__ = lambda self: self.name


def _patch_autosummary():
    import sphinx
    from sphinx.ext import autosummary
    from sphinx.ext.autosummary import generate

    def get_documenter(*args, **kwargs):
        if hasattr(autosummary, "_get_documenter"):
            obj = args[0]  # signature is (obj, parent, *, registry)
            get_documenter = autosummary._get_documenter
        else:
            obj = args[1]  # signature is (app, obj, parent)
            get_documenter = autosummary.get_documenter
        if isinstance(obj, type) and issubclass(obj, Exception):
            if sphinx.version_info < (9, 0):
                return types.SimpleNamespace(objtype="class")
            return "class"
        return get_documenter(*args, **kwargs)

    if hasattr(generate, "_get_documenter"):
        generate._get_documenter = get_documenter
    else:
        generate.get_documenter = get_documenter

    def generate_autosummary_content(
        name, obj, parent, template, template_name, *args, **kwargs
    ):
        if isinstance(obj, type) and issubclass(obj, Exception):
            template_name = template_name or "exception"
        return generate_autosummary_content_orig(
            name, obj, parent, template, template_name, *args, **kwargs
        )

    generate_autosummary_content_orig = generate.generate_autosummary_content
    generate.generate_autosummary_content = generate_autosummary_content


def _patch_autodoc():
    try:
        import sphinx.ext.autodoc._dynamic._loader as mod
    except ImportError:
        return

    class TypeAliasWrapper:
        def __init__(self, obj):
            self._wrapped_obj = obj

        def __getattribute__(self, name):
            obj = super().__getattribute__("_wrapped_obj")
            return obj if name == "__value__" else getattr(obj, name)

    def make_props_from_imported_object(im, **kwargs):
        obj = im.obj
        if kwargs["objtype"] == "type":
            im.obj = TypeAliasWrapper(im.obj)
        try:
            return make_props_from_imported_object_orig(im, **kwargs)
        finally:
            im.obj = obj

    make_props_from_imported_object_orig = mod._make_props_from_imported_object
    mod._make_props_from_imported_object = make_props_from_imported_object


def _setup_autodoc(app):
    from sphinx.ext import autodoc
    from sphinx.locale import _
    from sphinx.util.typing import restify

    def istypealias(obj, name):
        if isinstance(obj, type):
            return name != getattr(obj, "__name__", None)
        return obj == typing.Any

    def istypevar(obj):
        return isinstance(obj, typing.TypeVar)

    class TypeDocumenter(autodoc.DataDocumenter):
        objtype = "type"
        directivetype = "data"
        priority = autodoc.ClassDocumenter.priority + 1

        @classmethod
        def can_document_member(cls, member, membername, _isattr, parent):
            return (
                isinstance(parent, autodoc.ModuleDocumenter)
                and parent.name == "mpi4py.typing"
                and (istypevar(member) or istypealias(member, membername))
            )

        def add_directive_header(self, sig):
            if istypevar(self.object):
                obj = self.object
                if not self.options.annotation:
                    self.options.annotation = f' = TypeVar("{obj.__name__}")'
            super().add_directive_header(sig)

        def update_content(self, more_content):
            obj = self.object
            if istypevar(obj):
                if obj.__covariant__:
                    kind = _("Covariant")
                elif obj.__contravariant__:
                    kind = _("Contravariant")
                else:
                    kind = _("Invariant")
                content = f"{kind} :class:`~typing.TypeVar`."
                more_content.append(content, "")
                more_content.append("", "")
            if istypealias(obj, self.name):
                content = _("alias of %s") % restify(obj)
                more_content.append(content, "")
                more_content.append("", "")
            super().update_content(more_content)

        def get_doc(self, *args, **kwargs):
            obj = self.object
            if istypevar(obj):
                if obj.__doc__ == typing.TypeVar.__doc__:
                    return []
            return super().get_doc(*args, **kwargs)

    app.add_autodocumenter(TypeDocumenter)


def setup(app):
    import sphinx

    _setup_numpy_typing()
    _patch_domain_python()
    if sphinx.version_info < (9, 1):
        _patch_autosummary()
        _patch_autodoc()
    if sphinx.version_info < (9, 0):
        _setup_autodoc(app)

    try:
        from mpi4py import MPI
    except ImportError:
        autodoc_mock_imports.append("mpi4py")
        return

    sys_dwb = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    apidoc = __import__("apidoc")
    sys.dont_write_bytecode = sys_dwb

    del MPI.memory  # TODO
    name = MPI.__name__
    here = pathlib.Path(__file__).resolve().parent
    outdir = here / apidoc.OUTDIR
    source = outdir / f"{name}.py"
    getmtime = os.path.getmtime
    generate = (
        not source.exists()
        or getmtime(source) < getmtime(MPI.__file__)
        or getmtime(source) < getmtime(apidoc.__file__)
    )
    if generate:
        apidoc.generate(source)
    module = apidoc.load_module(source)
    module.Get_version.__code__ = (lambda: (4, 0)).__code__
    apidoc.replace_module(module)

    synopsis = autosummary_context["synopsis"]
    synopsis[module.__name__] = module.__doc__.strip()

    modules = [
        "mpi4py",
        "mpi4py.run",
        "mpi4py.util.dtlib",
        "mpi4py.util.pkl5",
        "mpi4py.util.pool",
        "mpi4py.util.sync",
    ]
    if sphinx.version_info < (9, 0):
        typing_overload = typing.overload
        typing.overload = lambda arg: arg
    for name in modules:
        mod = importlib.import_module(name)
        ann = apidoc.load_module(f"{mod.__file__}i", name)
        apidoc.annotate(mod, ann)
    if sphinx.version_info < (9, 0):
        typing.overload = typing_overload


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = (
    "sphinx_rtd_theme" if "sphinx_rtd_theme" in extensions else "default"
)

html_logo = "../mpi4py.svg"

html_favicon = "../mpi4py.svg"

if html_theme == "default":
    html_copy_source = False


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = f"{package}-man"


# -- Options for LaTeX output ---------------------------------------------

# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ("index", f"{package}.tex", project, author, "howto"),
]

latex_elements = {
    "papersize": "a4",
}


# -- Options for manual page output ---------------------------------------

# (source start file, name, description, authors, manual section).
man_pages = [("index", package, project, [author], 3)]


# -- Options for Texinfo output -------------------------------------------

# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        package,
        project,
        author,
        package,
        f"{project}.",
        "Miscellaneous",
    ),
]


# -- Options for Epub output ----------------------------------------------

# Output file base name for ePub builder.
epub_basename = package
