# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Typing support."""

from typing import (
    Any,
    Union,
    List,
    Tuple,
    Sequence,
)
from numbers import (
    Integral,
)
from .MPI import (
    Datatype,
    BottomType,
    InPlaceType,
)

__all__ = [
    'Buffer',
    'Bottom',
    'InPlace',
    'Aint',
    'Count',
    'Displ',
    'Offset',
    'TypeSpec',
    'BufSpec',
    'BufSpecB',
    'BufSpecV',
    'BufSpecW',
    'TargetSpec',
]


Buffer = Any
"""
Buffer-like object.
"""


Bottom = Union[BottomType, None]
"""
Start of the address range.
"""


InPlace = Union[InPlaceType, None]
"""
In-place buffer argument.
"""


Aint = Integral
"""
Address-sized integral type.
"""


Count = Integral
"""
Integral type for counts.
"""


Displ = Integral
"""
Integral type for displacements.
"""


Offset = Integral
"""
Integral type for offsets.
"""


TypeSpec = Union[Datatype, str]
"""
Datatype specification.
"""


BufSpec = Union[
    Buffer,
    Tuple[Buffer, Count],
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Count, TypeSpec],
    Tuple[Bottom, Count, Datatype],
    List,
]
"""
Buffer specification.

* `Buffer`
* Tuple[`Buffer`, `Count`]
* Tuple[`Buffer`, `TypeSpec`]
* Tuple[`Buffer`, `Count`, `TypeSpec`]
* Tuple[`Bottom`, `Count`, `Datatype`]
"""


BufSpecB = Union[
    Buffer,
    Tuple[Buffer, Count],
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Count, TypeSpec],
    List,
]
"""
Buffer specification (block).

* `Buffer`
* Tuple[`Buffer`, `Count`]
* Tuple[`Buffer`, `TypeSpec`]
* Tuple[`Buffer`, `Count`, `TypeSpec`]
"""


BufSpecV = Union[
    Buffer,
    Tuple[Buffer, Sequence[Count]],
    Tuple[Buffer, Tuple[Sequence[Count], Sequence[Displ]]],
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Sequence[Count], TypeSpec],
    Tuple[Buffer, Tuple[Sequence[Count], Sequence[Displ]], TypeSpec],
    Tuple[Buffer, Sequence[Count], Sequence[Displ], TypeSpec],
    List,
]
"""
Buffer specification (vector).

* `Buffer`
* Tuple[`Buffer`, Sequence[`Count`]]
* Tuple[`Buffer`, Tuple[Sequence[`Count`], Sequence[`Displ`]]]
* Tuple[`Buffer`, `TypeSpec`]
* Tuple[`Buffer`, Sequence[`Count`], `TypeSpec`]
* Tuple[`Buffer`, Tuple[Sequence[`Count`], Sequence[`Displ`]], `TypeSpec`]
* Tuple[`Buffer`, Sequence[`Count`], Sequence[`Displ`], `TypeSpec`]
"""


BufSpecW = Union[
    Tuple[Buffer, Sequence[Datatype]],
    Tuple[Buffer, Tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    Tuple[Buffer, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    List,
]
"""
Buffer specification (generalized).

* Tuple[`Buffer`, Sequence[`Datatype`]]
* Tuple[`Buffer`, \
        Tuple[Sequence[`Count`], Sequence[`Displ`]], Sequence[`Datatype`]]
* Tuple[`Buffer`, Sequence[`Count`], Sequence[`Displ`], Sequence[`Datatype`]]
"""


TargetSpec = Union[
    Displ,
    Tuple[()],
    Tuple[Displ],
    Tuple[Displ, Count],
    Tuple[Displ, Count, TypeSpec],
    List,
]
"""
Target specification.

* `Displ`
* Tuple[()]
* Tuple[`Displ`]
* Tuple[`Displ`, `Count`]
* Tuple[`Displ`, `Count`, `Datatype`]
"""
