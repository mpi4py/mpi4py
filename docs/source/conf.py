# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
import typing
import datetime
import importlib
sys.path.insert(0, os.path.abspath('.'))
_today = datetime.datetime.now()


# -- Project information -----------------------------------------------------

package = 'mpi4py'


def pkg_version():
    import re
    here = os.path.dirname(__file__)
    pardir = [os.path.pardir] * 2
    topdir = os.path.join(here, *pardir)
    srcdir = os.path.join(topdir, 'src')
    with open(os.path.join(srcdir, 'mpi4py', '__init__.py')) as f:
        m = re.search(r"__version__\s*=\s*'(.*)'", f.read())
        return m.groups()[0]


project = 'MPI for Python'
author = 'Lisandro Dalcin'
copyright = f'{_today.year}, {author}'

# The full version, including alpha/beta/rc tags
release = pkg_version()
version = release.rsplit('.', 1)[0]


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

default_role = 'any'

nitpicky = True
nitpick_ignore = [
    ('c:func', r'atexit'),
    ('py:mod', r'__worker__'),
    ('py:mod', r'pickle5'),
]
nitpick_ignore_regex = [
    (r'c:.*', r'MPI_.*'),
    (r'envvar', r'MPI(CC|LD|CFG)'),
    (r'envvar', r'(LD_LIBRARY_)?PATH'),
    (r'envvar', r'(MPICH|OMPI|MPIEXEC)_.*'),
]
# python_use_unqualified_type_names = True

autodoc_typehints = 'description'
autodoc_type_aliases = {}
autodoc_mock_imports = []

autosummary_context = {
    'synopsis': {},
    'autotype': {},
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

napoleon_preprocess_types = True

try:
    import sphinx_rtd_theme
    if 'sphinx_rtd_theme' not in extensions:
        extensions.append('sphinx_rtd_theme')
except ImportError:
    sphinx_rtd_theme = None


def _setup_numpy_typing():
    try:
        import numpy as np
    except ImportError:
        np = type(sys)('numpy')
        sys.modules[np.__name__] = np
        np.dtype = type('dtype', (), {})

    try:
        import numpy.typing as npt
    except ImportError:
        npt = type(sys)('numpy.typing')
        np.typing = npt
        sys.modules[npt.__name__] = npt
        npt.__all__ = []
        for attr in ['ArrayLike', 'DTypeLike']:
            setattr(npt, attr, typing.Any)
            npt.__all__.append(attr)

    autodoc_type_aliases.update({
        'dtype': 'numpy.dtype',
        'ArrayLike': 'numpy.typing.ArrayLike',
        'DTypeLike': 'numpy.typing.DTypeLike',
    })


def _patch_domain_python():
    from sphinx.domains import python
    try:
        from numpy.typing import __all__ as numpy_types
    except ImportError:
        numpy_types = []
    try:
        from mpi4py.typing import __all__ as mpi4py_types
    except ImportError:
        mpi4py_types = []

    def make_xref(self, rolename, domain, target, *args, **kwargs):
        if target in ('True', 'False'):
            rolename = 'obj'
        elif target in numpy_types:
            rolename = 'data'
        elif target in mpi4py_types:
            rolename = 'data'
        return make_xref_orig(self, rolename, domain, target, *args, *kwargs)

    numpy_types = set(f'numpy.typing.{name}' for name in numpy_types)
    mpi4py_types = set(mpi4py_types)
    make_xref_orig = python.PyXrefMixin.make_xref
    python.PyXrefMixin.make_xref = make_xref


def _setup_autodoc(app):
    from sphinx.locale import _
    from sphinx.util.typing import restify
    from sphinx.ext.autodoc import ModuleDocumenter
    from sphinx.ext.autodoc import ClassDocumenter
    from sphinx.ext.autodoc import DataDocumenter

    def istypealias(obj):
        if isinstance(obj, type):
            return True
        return obj in (
            typing.Any,
        )

    class TypeDocumenter(DataDocumenter):
        objtype = 'type'
        directivetype = 'data'
        priority = ClassDocumenter.priority + 1

        @classmethod
        def can_document_member(cls, member, membername, isattr, parent):
            return (isinstance(parent, ModuleDocumenter) and
                    parent.name == 'mpi4py.typing' and
                    istypealias(member))

        def update_content(self, more_content):
            if istypealias(self.object):
                more_content.append(
                    _('alias of %s') % restify(self.object), '')
                more_content.append('', '')
            super().update_content(more_content)

    app.add_autodocumenter(TypeDocumenter)


def _patch_autosummary():
    from sphinx.ext import autodoc
    from sphinx.ext import autosummary
    from sphinx.ext.autosummary import generate

    class ExceptionDocumenter(autodoc.ExceptionDocumenter):
        objtype = 'class'

    def get_documenter(app, obj, parent):
        if isinstance(obj, type) and issubclass(obj, BaseException):
            caller = sys._getframe().f_back.f_code.co_name
            if caller == 'generate_autosummary_content':
                if obj.__module__ == 'mpi4py.MPI':
                    if obj.__name__ == 'Exception':
                        return ExceptionDocumenter
        return autosummary.get_documenter(app, obj, parent)

    generate.get_documenter = get_documenter


def setup(app):
    _setup_numpy_typing()
    _patch_domain_python()
    _setup_autodoc(app)
    _patch_autosummary()

    try:
        from mpi4py import MPI
    except ImportError:
        autodoc_mock_imports.append('mpi4py')
        return

    sys_dwb = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    import apidoc
    sys.dont_write_bytecode = sys_dwb

    name = MPI.__name__
    here = os.path.abspath(os.path.dirname(__file__))
    outdir = os.path.join(here, apidoc.OUTDIR)
    source = os.path.join(outdir, f'{name}.py')
    getmtime = os.path.getmtime
    generate = (
        not os.path.exists(source)
        or getmtime(source) < getmtime(MPI.__file__)
        or getmtime(source) < getmtime(apidoc.__file__)
    )
    if generate:
        apidoc.generate(source)
    module = apidoc.load_module(source)
    apidoc.replace_module(module)

    synopsis = autosummary_context['synopsis']
    synopsis[module.__name__] = module.__doc__.strip()
    autotype = autosummary_context['autotype']
    autotype[module.Exception.__name__] = 'exception'

    mod = importlib.import_module('mpi4py.typing')
    for name in mod.__all__:
        autodoc_type_aliases[name] = f'{name}'

    mod = importlib.import_module('mpi4py.MPI')
    for name in dir(mod):
        attr = getattr(mod, name)
        if isinstance(attr, type):
            if attr.__module__ == mod.__name__:
                autodoc_type_aliases[name] = f'{name}'

    modules = [
        'mpi4py',
        'mpi4py.run',
        'mpi4py.util.dtlib',
        'mpi4py.util.pkl5',
    ]
    typing_overload = typing.overload
    typing.overload = lambda arg: arg
    for name in modules:
        mod = importlib.import_module(name)
        ann = apidoc.load_module(f'{mod.__file__}i', name)
        apidoc.annotate(mod, ann)
    typing.overload = typing_overload


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = (
    'sphinx_rtd_theme' if 'sphinx_rtd_theme' in extensions else 'default'
)

if html_theme == 'default':
    html_copy_source = False

if html_theme == 'sphinx_rtd_theme':
    html_theme_options = {
        'analytics_id': 'UA-48837848-1',
    }

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

if html_theme == 'sphinx_rtd_theme':
    html_css_files = [
        'css/custom.css',
    ]


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = f'{package}-man'


# -- Options for LaTeX output ---------------------------------------------

# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ('index', f'{package}.tex', project, author, 'howto'),
]

latex_elements = {
    'papersize': 'a4',
}


# -- Options for manual page output ---------------------------------------

# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', package, project, [author], 3)
]


# -- Options for Texinfo output -------------------------------------------

# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', package, project, author,
     package, f'{project}.', 'Miscellaneous'),
]


# -- Options for Epub output ----------------------------------------------

# Output file base name for ePub builder.
epub_basename = package
