# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
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
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

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

release = pkg_version()
version = release.rsplit('.', 1)[0]


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

needs_sphinx = '5.0.0'

default_role = 'any'

nitpicky = True
nitpick_ignore = [
    ('c:func', r'atexit'),
    ('py:mod', r'__worker__'),
    ('py:mod', r'pickle5'),
]
nitpick_ignore_regex = [
    (r'c:.*', r'MPI_.*'),
    (r'envvar', r'(LD_LIBRARY_)?PATH'),
    (r'envvar', r'(MPICH|OMPI|MPIEXEC)_.*'),
]

toc_object_entries = False
toc_object_entries_show_parents = 'hide'
# python_use_unqualified_type_names = True

autodoc_class_signature = 'separated'
autodoc_typehints = 'description'
autodoc_typehints_format = 'short'
autodoc_mock_imports = []
autodoc_type_aliases = {}

autosummary_context = {
    'synopsis': {},
    'autotype': {},
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'dlpack': ('https://dmlc.github.io/dlpack/latest/', None),
    'numba': ('https://numba.readthedocs.io/en/stable/', None),
}

napoleon_preprocess_types = True

try:
    import sphinx_rtd_theme
    if 'sphinx_rtd_theme' not in extensions:
        extensions.append('sphinx_rtd_theme')
except ImportError:
    sphinx_rtd_theme = None

try:
    import sphinx_copybutton
    if 'sphinx_copybutton' not in extensions:
        extensions.append('sphinx_copybutton')
except ImportError:
    sphinx_copybutton = None

copybutton_exclude = '.linenos, .gp, .go'
copybutton_prompt_text = r'\$ |>>> |\.\.\. '
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = '\\'


def _setup_numpy_typing():
    try:
        import numpy as np
    except ImportError:
        from types import new_class
        from typing import Generic, TypeVar
        np = type(sys)('numpy')
        sys.modules[np.__name__] = np
        np.dtype = new_class('dtype', (Generic[TypeVar('T')],))
        np.dtype.__module__ = np.__name__

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
        autodoc_type_aliases[name] = f'~numpy.typing.{name}'
    for name in mpi4py_types:
        autodoc_type_aliases[name] = f'~mpi4py.typing.{name}'

    from sphinx.domains.python import PythonDomain
    PythonDomain.object_types['data'].roles += ('class',)


def _setup_autodoc(app):
    from sphinx.ext import autodoc
    from sphinx.ext import autosummary
    from sphinx.util import typing
    from sphinx.locale import _

    #

    class ClassDocumenterMixin:

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.config.autodoc_class_signature == 'separated':
                members = self.options.members
                special_members = self.options.special_members
                if special_members is not None:
                    for name in ('__new__', '__init__'):
                        if name in members:
                            members.remove(name)
                        if name in special_members:
                            special_members.remove(name)

    class ClassDocumenter(
        ClassDocumenterMixin,
        autodoc.ClassDocumenter,
    ):
        pass

    class ExceptionDocumenter(
        ClassDocumenterMixin,
        autodoc.ExceptionDocumenter,
    ):
        pass

    app.add_autodocumenter(ClassDocumenter, override=True)
    app.add_autodocumenter(ExceptionDocumenter, override=True)

    #

    def istypealias(obj):
        if isinstance(obj, type):
            return True
        return obj in (
            typing.Any,
        )

    class TypeDocumenter(autodoc.DataDocumenter):
        objtype = 'type'
        directivetype = 'data'
        priority = autodoc.ClassDocumenter.priority + 1

        @classmethod
        def can_document_member(cls, member, membername, isattr, parent):
            return (
                isinstance(parent, autodoc.ModuleDocumenter)
                and parent.name == 'mpi4py.typing'
                and istypealias(member)
            )

        def update_content(self, more_content):
            if istypealias(self.object):
                more_content.append(
                    _('alias of %s') % typing.restify(self.object), '')
                more_content.append('', '')
            super().update_content(more_content)

    app.add_autodocumenter(TypeDocumenter)

    #

    class ExceptionDocumenterCustom(ExceptionDocumenter):
        objtype = 'class'

    def get_documenter(app, obj, parent):
        if isinstance(obj, type) and issubclass(obj, BaseException):
            caller = sys._getframe().f_back.f_code.co_name
            if caller == 'generate_autosummary_content':
                if obj.__module__ == 'mpi4py.MPI':
                    if obj.__name__ == 'Exception':
                        return ExceptionDocumenterCustom
        return autosummary.get_documenter(app, obj, parent)

    from sphinx.ext.autosummary import generate
    generate.get_documenter = get_documenter


def setup(app):
    _setup_numpy_typing()
    _patch_domain_python()
    _setup_autodoc(app)

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
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = (
    'sphinx_rtd_theme' if 'sphinx_rtd_theme' in extensions else 'default'
)

if html_theme == 'default':
    html_copy_source = False

if html_theme == 'sphinx_rtd_theme':
    html_theme_options = {
        'analytics_id': 'UA-48837848-1',
    }

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
