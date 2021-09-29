import os
import sys
import inspect
from textwrap import dedent
from textwrap import indent


def is_function(obj):
    return inspect.isbuiltin(obj) or type(obj) is type(ord)


def is_method(obj):
    return inspect.ismethoddescriptor(obj) or type(obj) in (
        type(str.index),
        type(str.__add__),
        type(str.__new__),
    )


def is_classmethod(obj):
    return inspect.isbuiltin(obj) or type(obj).__name__ in (
        'classmethod',
        'classmethod_descriptor',
    )


def is_staticmethod(obj):
    return type(obj).__name__ in (
        'staticmethod',
    )


def is_datadescr(obj):
    return inspect.isdatadescriptor(obj) and not hasattr(obj, 'fget')


def is_property(obj):
    return inspect.isdatadescriptor(obj) and hasattr(obj, 'fget')


def is_class(obj):
    return inspect.isclass(obj) or type(obj) is type(int)


class Lines(list):

    INDENT = " " * 4
    level = 0

    @property
    def add(self):
        return self

    @add.setter
    def add(self, lines):
        if lines is None:
            return
        if isinstance(lines, str):
            lines = dedent(lines).strip().split("\n")
        indent = self.INDENT * self.level
        for line in lines:
            self.append(indent + line)


def signature(obj):
    doc = obj.__doc__
    sig = doc.split('\n', 1)[0].split('.', 1)[-1]
    return sig


def docstring(obj):
    doc = obj.__doc__
    doc = doc.split('\n', 1)[1]
    doc = dedent(doc).strip()
    doc = f'"""{doc}"""'
    doc = indent(doc, Lines.INDENT)
    return doc


def apidoc_constant(constant):
    name, value = constant
    typename = type(value).__name__
    init = f"_def({typename}, '{name}')"
    doc = f"#: :class:`{typename}` ``{name}``"
    return f"{name}: {typename} = {init}  {doc}\n"


def apidoc_function(function):
    sig = signature(function)
    doc = docstring(function)
    body = Lines.INDENT + "..."
    return f"def {sig}:\n{doc}\n{body}\n"


def apidoc_method(method):
    sig = signature(method)
    doc = docstring(method)
    body = Lines.INDENT + "..."
    return f"def {sig}:\n{doc}\n{body}\n"


def apidoc_datadescr(datadescr, name=None):
    sig = signature(datadescr)
    doc = docstring(datadescr)
    name = sig.split(':')[0].strip()
    type = sig.split(':')[1].strip()
    sig = f"{name}(self) -> {type}"
    body = Lines.INDENT + "..."
    return f"@property\ndef {sig}:\n{doc}\n{body}\n"


def apidoc_property(prop, name=None):
    sig = signature(prop.fget)
    name = name or prop.fget.__name__
    type = sig.rsplit('->', 1)[-1].strip()
    sig = f"{name}(self) -> {type}"
    doc = f'"""{prop.__doc__}"""'
    doc = indent(doc, Lines.INDENT)
    body = Lines.INDENT + "..."
    return f"@property\ndef {sig}:\n{doc}\n{body}\n"


def apidoc_constructor(cls, name='__init__'):
    init = (name == '__init__')
    argname = cls.__mro__[-2].__name__.lower()
    argtype = cls.__name__
    initarg = f"{argname}: Optional[{argtype}] = None"
    selfarg = 'self' if init else 'cls'
    rettype = 'None' if init else argtype
    arglist = f"{selfarg}, {initarg}"
    sig = f"{name}({arglist}) -> {rettype}"
    ret = '...' if init else 'return super().__new__(cls)'
    body = Lines.INDENT + ret
    return f"def {sig}:\n{body}"


def apidoc_class(cls, done=None):
    skip = {
        '__doc__',
        '__module__',
        '__weakref__',
        '__pyx_vtable__',
        '__lt__',
        '__le__',
        '__ge__',
        '__gt__',
    }
    special = {
        '__len__': "__len__(self) -> int",
        '__bool__': "__bool__(self) -> bool",
        '__hash__': "__hash__(self) -> int",
        '__int__': "__int__(self) -> int",
        '__index__': "__int__(self) -> int",
        '__str__': "__str__(self) -> str",
        '__repr__': "__repr__(self) -> str",
        '__eq__': "__eq__(self, other: Any) -> bool",
        '__ne__': "__ne__(self, other: Any) -> bool",
    }
    constructor = {
        '__new__',
        '__init__',
    }

    override = OVERRIDE.get(cls.__name__, {})
    done = set() if done is None else done
    lines = Lines()

    base = cls.__base__
    if base is object:
        lines.add = f"class {cls.__name__}:"
    else:
        lines.add = f"class {cls.__name__}({base.__name__}):"
    lines.level += 1

    doc = cls.__doc__
    doc = dedent(doc).strip()
    if doc.startswith(f"{cls.__name__}("):
        doc = doc.split('\n', 1)[1].strip()
    lines.add = f'"""{doc}"""'

    for name in constructor:
        if name in override:
            done.update(constructor)
            lines.add = override[name]
            break
    for name in constructor:
        if name in done:
            break
        if name in cls.__dict__:
            done.update(constructor)
            lines.add = apidoc_constructor(cls, name)
            break

    if '__hash__' in cls.__dict__:
        if cls.__hash__ is None:
            done.add('__hash__')

    dct = cls.__dict__
    keys = list(dct.keys())
    for name in keys:
        if name in done:
            continue

        if name in skip:
            continue

        if name in override:
            done.add(name)
            lines.add = override[name]
            continue

        if name in special:
            done.add(name)
            sig = special[name]
            lines.add = f"def {sig}: ..."
            continue

        if name in constructor:
            done.update(constructor)
            lines.add = apidoc_constructor(cls)
            continue

        attr = getattr(cls, name)

        if is_method(attr):
            done.add(name)
            if name == attr.__name__:
                obj = dct[name]
                if is_classmethod(obj):
                    lines.add = f"@classmethod"
                elif is_staticmethod(obj):
                    lines.add = f"@staticmethod"
                lines.add = apidoc_method(attr)
            elif False:
                lines.add = f"{name} = {attr.__name__}"
            continue

        if is_datadescr(attr):
            done.add(name)
            lines.add = apidoc_datadescr(attr)
            continue

        if is_property(attr):
            done.add(name)
            lines.add = apidoc_property(attr, name)
            continue

    leftovers = [name for name in keys if
                 name not in done and name not in skip]
    assert not leftovers, f"leftovers: {leftovers}"

    lines.level -= 1
    return lines


def apidoc_module(module, done=None):
    skip = {
        '__doc__',
        '__name__',
        '__loader__',
        '__spec__',
        '__file__',
        '__package__',
        '__builtins__',
        '__pyx_capi__',
    }

    done = set() if done is None else done
    lines = Lines()

    keys = list(module.__dict__.keys())
    keys.sort(key=lambda name: name.startswith("_"))

    constants = [
        (name, getattr(module, name)) for name in keys
        if all((
            name not in done and name not in skip,
            isinstance(getattr(module, name), int),
        ))
    ]
    for attr in constants:
        name, value = attr
        done.add(name)
        if name in OVERRIDE:
            lines.add = OVERRIDE[name]
        else:
            lines.add = apidoc_constant((name, value))
    if constants:
        lines.add = ""

    for name in keys:
        if name in done or name in skip:
            continue
        value = getattr(module, name)

        if is_class(value):
            done.add(name)
            lines.add = apidoc_class(value)
            lines.add = ""
            instances = [
                (k, getattr(module, k)) for k in keys
                if all((
                    k not in done and k not in skip,
                    type(getattr(module, k)) is value,
                ))
            ]
            for attrname, attrvalue in instances:
                done.add(attrname)
                lines.add = apidoc_constant((attrname, attrvalue))
            if instances:
                lines.add = ""
            continue

        if is_function(value):
            done.add(name)
            if name == value.__name__:
                lines.add = apidoc_function(value)
            else:
                lines.add = f"{name} = {value.__name__}"
            continue

    lines.add = ""
    for name in keys:
        if name in done or name in skip:
            continue
        value = getattr(module, name)
        done.add(name)
        if name in OVERRIDE:
            lines.add = OVERRIDE[name]
        else:
            lines.add = apidoc_constant((name, value))

    leftovers = [name for name in keys if
                 name not in done and name not in skip]
    assert not leftovers, f"leftovers: {leftovers}"
    return lines


IMPORTS = """
from __future__ import annotations
"""

HELPERS = """
class _Int(int): pass

class Bottom(_Int): pass

class InPlace(_Int): pass

def _repr(obj):
    try:
        return obj._repr
    except AttributeError:
        return super(obj).__repr__()

def _def(cls, name):
    if cls is int:
       cls = _Int
    obj = cls()
    if cls.__name__ in ('Pickle', 'memory'):
        return obj
    obj._repr = name
    if '__repr__' not in cls.__dict__:
        cls.__repr__ = _repr
    return obj
"""

OVERRIDE = {
    'Exception': {
        '__new__':(
            "def __new__(cls, ierr: int = SUCCESS) -> Exception:\n"
            "    return super().__new__(ierr)"),
        "__lt__": "def __lt__(self, other: int) -> bool: ...",
        "__le__": "def __le__(self, other: int) -> bool: ...",
        "__gt__": "def __gt__(self, other: int) -> bool: ...",
        "__ge__": "def __ge__(self, other: int) -> bool: ...",
    },
    'Info': {
        '__iter__':
        "def __iter__(self) -> Iterator[str]: ...",
        '__getitem__':
        "def __getitem__(self, item: str) -> str: ...",
        '__setitem__':
        "def __setitem__(self, item: str, value: str) -> None: ...",
        '__delitem__':
        "def __delitem__(self, item: str) -> None: ...",
        '__contains__':
        "def __contains__(self, value: str) -> bool: ...",
    },
    'Op': {
        '__call__': "def __call__(self, x: Any, y: Any) -> Any: ...",
    },
    'memory': {
        '__new__':(
            "def __new__(cls, buf: Buffer) -> memory:\n"
            "    return super().__new__()"),
        '__getitem__': (
            "def __getitem__(self, "
            "item: Union[int, slice]) "
            "-> Union[int, memory]: ..."),
        '__setitem__': (
            "def __setitem__(self, "
            "item: Union[int, slice], "
            "value: Union[int, Buffer]) "
            "-> None: ..."),
        '__delitem__': None,
    },
    'Pickle': {
        '__init__': """
        def __init__(self,
            dumps: Optional[Callable[[Any, int], bytes]] = None,
            loads: Optional[Callable[[Buffer], Any]] = None,
            protocol: Optional[int] = None,
        ) -> None: ...
        """
    },
    '_typedict': "_typedict: Dict[str, Datatype] = {}",
    '_typedict_c': "_typedict_c: Dict[str, Datatype] = {}",
    '_typedict_f': "_typedict_f: Dict[str, Datatype] = {}",
    '_keyval_registry': None,
}


def apidoc_mpi4py_MPI(done=None):
    from mpi4py import MPI
    lines = Lines()
    lines.add = f'"""{MPI.__doc__}"""'
    lines.add = IMPORTS
    lines.add = ""
    lines.add = HELPERS
    lines.add = ""
    lines.add = apidoc_module(MPI)
    return lines


def generate(filename):
    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)
    with open(filename, 'w') as f:
        for line in apidoc_mpi4py_MPI():
            print(line, file=f)


def load_module(filename, name=None):
    if name is None:
        name, _ = os.path.splitext(
            os.path.basename(filename))
    module = type(sys)(name)
    module.__file__ = filename
    module.__package__ = name.rsplit('.', 1)[0]
    with open(filename) as f:
        exec(f.read(), module.__dict__)
    return module


_sys_modules = {}


def replace_module(module):
    name = module.__name__
    assert name not in _sys_modules
    _sys_modules[name] = sys.modules[name]
    sys.modules[name] = module


def restore_module(module):
    name = module.__name__
    assert name in _sys_modules
    sys.modules[name] = _sys_modules[name]


def annotate(dest, source):
    try:
        dest.__annotations__ = source.__annotations__
    except Exception:
        pass
    if isinstance(dest, type):
        for name in dest.__dict__.keys():
            if hasattr(source, name):
                obj = getattr(dest, name)
                annotate(obj, getattr(source, name))
    if isinstance(dest, type(sys)):
        for name in dir(dest):
            if hasattr(source, name):
                obj = getattr(dest, name)
                mod = getattr(obj, '__module__', None)
                if dest.__name__ == mod:
                    annotate(obj, getattr(source, name))


OUTDIR = 'reference'

if __name__ == '__main__':
    generate(os.path.join(OUTDIR, 'mpi4py.MPI.py'))
