import collections
import inspect
import pathlib
import textwrap

from mpi4py import MPI


def is_cyfunction(obj):
    return type(obj).__name__ == "cython_function_or_method"


def is_function(obj):
    return (
        inspect.isbuiltin(obj)
        or is_cyfunction(obj)
        or type(obj) is type(ord)
    )  # fmt: skip


def is_method(obj):
    return (
        inspect.ismethoddescriptor(obj)
        or inspect.ismethod(obj)
        or is_cyfunction(obj)
        or type(obj) in (
            type(str.index),
            type(str.__add__),
            type(str.__new__),
        )
    )  # fmt: skip


def is_classmethod(obj):
    return (
        inspect.isbuiltin(obj)
        or type(obj).__name__ in (
            "classmethod",
            "classmethod_descriptor",
        )
    )  # fmt: skip


def is_staticmethod(obj):
    return type(obj).__name__ == "staticmethod"


def is_datadescr(obj):
    return inspect.isdatadescriptor(obj) and not hasattr(obj, "fget")


def is_property(obj):
    return inspect.isdatadescriptor(obj) and hasattr(obj, "fget")


def is_class(obj):
    return inspect.isclass(obj)


class Lines(collections.UserList):
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
            lines = textwrap.dedent(lines).strip().split("\n")
        indent = self.INDENT * self.level
        for line in lines:
            self.append(indent + line)


def signature(obj):
    doc = obj.__doc__
    sig = doc.partition("\n")[0]
    return sig or None


def docstring(obj):
    doc = obj.__doc__
    doc = doc.partition("\n")[2]
    doc = textwrap.dedent(doc).strip()
    doc = f'"""{doc}"""'
    doc = textwrap.indent(doc, Lines.INDENT)
    return doc


def visit_constant(constant):
    name, value = constant
    return f"{name}: Final[{type(value).__name__}] = ..."


def visit_function(function):
    fname = function.__name__
    fsign = inspect.signature(function)
    for name, param in fsign.parameters.items():
        value = param.default
        if value is param.empty:
            pass
        elif value is Ellipsis:
            param._default = "..."
        elif value in (None, ()):
            pass
        elif type(value) is bool:
            pass
        elif type(value).__module__ == "mpi4py.MPI":
            param._default = value.__reduce__()
        elif type(value) is str:
            param._default = f'"{value}"'
        elif type(value) is int:
            newvalue = ARGUMENTS.get((name, value))
            if newvalue is not None:
                param._default = newvalue
            elif value != 0 and name not in ("maxprocs", "disp_unit"):
                print(f"fn:{fname} arg:{name} default:{value}")
        else:
            print(f"fn:{fname} arg:{name} default:{value}")
    sig = str(fsign)
    sig = sig.replace("'", "")  # fix type annotations
    sig = sig.replace('"', "'")  # fix string quotation
    assert f"{fname}{sig}" == f"{signature(function)}"  # noqa: S101
    return f"def {fname}{sig}: ..."


def visit_method(method):
    return visit_function(method)


def visit_datadescr(datadescr):
    sig = signature(datadescr)
    return f"{sig}"


def visit_property(prop, name=None):
    gname = prop.fget.__name__
    pname = name or gname
    if pname == gname:
        return ["@property", visit_method(prop.fget)]
    else:
        return f"{pname} = property({gname})"


def visit_constructor(cls, name="__init__", args=None):
    init = name == "__init__"
    argname = cls.__name__.lower()
    argtype = cls.__name__
    initarg = args or f"{argname}: {argtype} | None = None"
    selfarg = "self" if init else "cls"
    rettype = "None" if init else "Self"
    arglist = f"{selfarg}, {initarg}"
    sig = f"{name}({arglist}) -> {rettype}"
    return f"def {sig}: ..."


def visit_class(cls, done=None):
    skip = {
        "__doc__",
        "__dict__",
        "__module__",
        "__weakref__",
        "__pyx_vtable__",
        "__str__",
        "__repr__",
        "__lt__",
        "__le__",
        "__ge__",
        "__gt__",
    }
    special = {
        "__len__": ("self", "int", None),
        "__bool__": ("self", "bool", None),
        "__hash__": ("self", "int", None),
        "__int__": ("self", "int", None),
        "__index__": ("self", "int", None),
        "__eq__": ("self", "other: object", "/", "bool", None),
        "__ne__": ("self", "other: object", "/", "bool", None),
        "__buffer__": ("self", "flags: int", "/", "memoryview", (3, 12)),
    }
    constructor = (
        "__new__",
        "__init__",
    )

    override = OVERRIDE.get(cls.__name__, {})
    done = set() if done is None else done
    lines = Lines()

    if cls.__name__ == "Exception":
        skip = skip - {f"__{a}{b}__" for a in "lg" for b in "et"}
        constructor = ()
    if "__hash__" in cls.__dict__:
        if cls.__hash__ is None:
            done.add("__hash__")

    try:
        type("sub", (cls,), {})
        final = False
    except TypeError:
        final = True
    if final:
        lines.add = "@final"
    base = cls.__base__
    if base is object:
        lines.add = f"class {cls.__name__}:"
    else:
        lines.add = f"class {cls.__name__}({base.__name__}):"
    lines.level += 1

    for name in constructor:
        if name in done:
            continue
        if name in override:
            done.add(name)
            lines.add = override[name]
            continue
        if name in cls.__dict__:
            done.add(name)
            lines.add = visit_constructor(cls, name)
            continue

    dct = cls.__dict__
    keys = list(dct.keys())
    for name in keys:
        if name in done:
            continue

        if name in override:
            done.add(name)
            lines.add = override[name]
            continue

        if name in skip:
            continue

        if name in special:
            done.add(name)
            *args, retv, py = special[name]
            sig = f"{name}({', '.join(args)}) -> {retv}"
            if py is not None:
                lines.add = f"if sys.version_info >= {py}:"
                lines.level += 1
            lines.add = f"def {sig}: ..."
            if py is not None:
                lines.level -= 1
            continue

        attr = getattr(cls, name)

        if is_method(attr):
            done.add(name)
            if name == attr.__name__:
                obj = dct[name]
                if is_classmethod(obj):
                    obj = obj.__func__
                    lines.add = "@classmethod"
                elif is_staticmethod(obj):
                    obj = obj.__func__
                    lines.add = "@staticmethod"
                lines.add = visit_method(obj)
            elif True:
                lines.add = f"{name} = {attr.__name__}"
            continue

        if is_datadescr(attr):
            done.add(name)
            lines.add = visit_datadescr(attr)
            continue

        if is_property(attr):
            done.add(name)
            lines.add = visit_property(attr, name)
            continue

    leftovers = [
        name for name in keys if name not in done and name not in skip
    ]
    if leftovers:
        raise RuntimeError(f"leftovers: {leftovers}")

    lines.level -= 1
    return lines


def visit_module(module, done=None):
    skip = {
        "__doc__",
        "__name__",
        "__loader__",
        "__spec__",
        "__file__",
        "__package__",
        "__builtins__",
    }

    done = set() if done is None else done
    lines = Lines()

    keys = list(module.__dict__.keys())
    keys.sort(key=lambda name: name.startswith("_"))

    constants = [
        (name, getattr(module, name))
        for name in keys
        if all((
            name not in done and name not in skip,
            isinstance(getattr(module, name), int),
        ))
    ]
    for name, value in constants:
        done.add(name)
        if name in OVERRIDE:
            lines.add = OVERRIDE[name]
        else:
            lines.add = visit_constant((name, value))
    if constants:
        lines.add = ""

    for name in keys:
        if name in done or name in skip:
            continue
        value = getattr(module, name)

        if is_class(value):
            done.add(name)
            lines.add = visit_class(value)
            lines.add = ""
            aliases = [
                (k, getattr(module, k))
                for k in keys
                if all((
                    k not in done and k not in skip,
                    getattr(module, k) is value,
                ))
            ]
            for aliasname, target in aliases:
                done.add(aliasname)
                lines.add = f"{aliasname} = {target.__name__}"
            if aliases:
                lines.add = ""
            instances = [
                (k, getattr(module, k))
                for k in keys
                if all((
                    k not in done and k not in skip,
                    type(getattr(module, k)) is value,
                ))
            ]
            for attrname, attrvalue in instances:
                done.add(attrname)
                lines.add = visit_constant((attrname, attrvalue))
            if instances:
                lines.add = ""
            continue

        if is_function(value):
            done.add(name)
            if name == value.__name__:
                lines.add = visit_function(value)
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
            lines.add = visit_constant((name, value))

    leftovers = [
        name for name in keys if name not in done and name not in skip
    ]
    if leftovers:
        raise RuntimeError(f"leftovers: {leftovers}")
    return lines


IMPORTS = """
import sys
from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from typing import (
    Any,
    AnyStr,
    Final,
    Literal,
    NoReturn,
    final,
    overload,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from os import PathLike
from threading import Lock
"""

ARGUMENTS = {
    (n, getattr(MPI, v)): v
    for n, v in (
        ("required", "THREAD_MULTIPLE"),
        ("order", "ORDER_C"),
        ("source", "ANY_SOURCE"),
        ("tag", "ANY_TAG"),
        ("sendtag", "ANY_TAG"),
        ("recvtag", "ANY_TAG"),
        ("amode", "MODE_RDONLY"),
        ("whence", "SEEK_SET"),
        ("lock_type", "LOCK_EXCLUSIVE"),
    )
}

OVERRIDE = {
    "Exception": {
        "__init__": "def __init__(self, ierr: int = SUCCESS, /) -> None: ...",
    },
    "Info": {
        "__iter__": "def __iter__(self) -> Iterator[str]: ...",
        "__getitem__": "def __getitem__(self, item: str, /) -> str: ...",
        "__setitem__": (
            "def __setitem__(self, item: str, value: str, /) -> None: ..."
        ),
        "__delitem__": "def __delitem__(self, item: str, /) -> None: ...",
        "__contains__": "def __contains__(self, value: str, /) -> bool: ...",
    },
    "Op": {
        "__call__": "def __call__(self, x: Any, y: Any, /) -> Any: ...",
    },
    "buffer": {
        "__new__": """
        @overload
        def __new__(cls) -> Self: ...
        @overload
        def __new__(cls, buf: Buffer, /) -> Self: ...
        """,
        "__getitem__": """
        @overload
        def __getitem__(self, item: int, /) -> int: ...
        @overload
        def __getitem__(self, item: slice, /) -> buffer: ...
        """,
        "__setitem__": """
        @overload
        def __setitem__(self, item: int, value: int, /) -> None: ...
        @overload
        def __setitem__(self, item: slice, value: Buffer, /) -> None: ...
        """,
        "__delitem__": None,
    },
    "Pickle": {
        "__new__": None,
        "__init__": """
        @overload
        def __init__(
            self,
            dumps: Callable[[Any, int], bytes],
            loads: Callable[[Buffer], Any],
            protocol: int | None = None,
            threshold: int | None = None,
        ) -> None: ...
        @overload
        def __init__(
            self,
            dumps: Callable[[Any], bytes] | None = None,
            loads: Callable[[Buffer], Any] | None = None,
        ) -> None: ...
        """,
    },
    "__pyx_capi__": "__pyx_capi__: Final[dict[str, Any]] = ...",
    "_typedict": "_typedict: Final[dict[str, Datatype]] = ...",
    "_typedict_c": "_typedict_c: Final[dict[str, Datatype]] = ...",
    "_typedict_f": "_typedict_f: Final[dict[str, Datatype]] = ...",
    "_keyval_registry": None,
}
OVERRIDE.update({
    subtype: {
        "__new__": "def __new__(cls) -> Self: ...",
    }
    for subtype in (
        "BottomType",
        "InPlaceType",
        "BufferAutomaticType",
    )
})  # fmt: skip
OVERRIDE.update({
    subtype: {
        "__new__": str.format("""
        def __new__(cls, {}: {} | None = None) -> Self: ...
        """, basetype.lower(), basetype)
    }
    for basetype, subtype in (
        ("Comm", "Comm"),
        ("Comm", "Intracomm"),
        ("Comm", "Topocomm"),
        ("Comm", "Cartcomm"),
        ("Comm", "Graphcomm"),
        ("Comm", "Distgraphcomm"),
        ("Comm", "Intercomm"),
        ("Request", "Request"),
        ("Request", "Prequest"),
        ("Request", "Grequest"),
    )
})  # fmt: skip
OVERRIDE.update({  # python/mypy#15717
    "Group": {
        "Intersect": """
        @classmethod  # python/mypy#15717
        def Intersect(cls, group1: Group, group2: Group) -> Self: ...
        """
    }
})  # fmt: skip

TYPING = """
from .typing import (  # noqa: E402,I001
    Buffer,
    Bottom,
    InPlace,
)
from .typing import (  # noqa: E402
    BufSpec,
    BufSpecB,
    BufSpecV,
    BufSpecW,
    TargetSpec,
)
"""


def visit_mpi4py_MPI():
    lines = Lines()
    lines.add = "# ruff: noqa: A001"
    lines.add = "# ruff: noqa: A002"
    lines.add = "# ruff: noqa: E501"
    lines.add = "# ruff: noqa: Q000"
    lines.add = "# fmt: off"
    lines.add = IMPORTS
    lines.add = ""
    lines.add = visit_module(MPI)
    lines.add = ""
    lines.add = TYPING
    return lines


def generate(filename):
    filename = pathlib.Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    with filename.open("w", encoding="utf-8") as f:
        script = pathlib.Path(__file__).name
        print(f"# Generated with `python conf/{script}`", file=f)
        for line in visit_mpi4py_MPI():
            print(line, file=f)


TOPDIR = pathlib.Path(__file__).resolve().parent.parent
OUTDIR = TOPDIR / "src" / "mpi4py"

if __name__ == "__main__":
    generate(OUTDIR / "MPI.pyi")
