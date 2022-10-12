# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Typing support."""
# pylint: disable=unnecessary-ellipsis
# pylint: disable=too-few-public-methods

import sys
from typing import (
    Any,
    Union,
    Optional,
    Sequence,
    List,
    Dict,
    Tuple,
)
from numbers import (
    Integral,
)
from .MPI import (
    Datatype,
    BottomType,
    InPlaceType,
)
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    try:
        from typing_extensions import Protocol
    except ImportError:
        Protocol = object
del sys

__all__ = [
    'SupportsBuffer',
    'SupportsDLPack',
    'SupportsCAI',
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


_Stream = Union[int, Any]
_PyCapsule = object
_DeviceType = int
_DeviceID = int


class SupportsBuffer(Protocol):
    """
    Python buffer protocol.

    .. seealso:: :ref:`python:bufferobjects`
    """

    def __buffer__(self, flags: int) -> memoryview:
        """Create a buffer from a Python object."""
        ...


class SupportsDLPack(Protocol):
    """
    DLPack data interchange protocol.

    .. seealso:: :ref:`dlpack:python-spec`
    """

    def __dlpack__(self, *, stream: Optional[_Stream] = None) -> _PyCapsule:
        """Export data for consumption as a DLPack capsule."""
        ...

    def __dlpack_device__(self) -> Tuple[_DeviceType, _DeviceID]:
        """Get device type and device ID in DLPack format."""
        ...


class SupportsCAI(Protocol):
    """
    CUDA Array Interface (CAI) protocol.

    .. seealso:: :ref:`numba:cuda-array-interface`
    """

    @property
    def __cuda_array_interface__(self) -> Dict[str, Any]:
        """CAI protocol data."""
        ...


Buffer = Union[
    SupportsBuffer,
    SupportsDLPack,
    SupportsCAI,
]
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
    Tuple[Bottom, Tuple[Sequence[Count], Sequence[Displ]], Datatype],
    Tuple[Bottom, Sequence[Count], Sequence[Displ], Datatype],
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
* Tuple[`Bottom`, Tuple[Sequence[`Count`], Sequence[`Displ`]], `Datatype`]
* Tuple[`Bottom`, Sequence[`Count`], Sequence[`Displ`], `Datatype`]
"""


BufSpecW = Union[
    Tuple[Buffer, Sequence[Datatype]],
    Tuple[Buffer, Tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    Tuple[Buffer, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    Tuple[Bottom, Tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    Tuple[Bottom, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    List,
]
"""
Buffer specification (generalized).

* Tuple[`Buffer`, Sequence[`Datatype`]]
* Tuple[`Buffer`, \
        Tuple[Sequence[`Count`], Sequence[`Displ`]], Sequence[`Datatype`]]
* Tuple[`Buffer`, Sequence[`Count`], Sequence[`Displ`], Sequence[`Datatype`]]
* Tuple[`Bottom`, \
        Tuple[Sequence[`Count`], Sequence[`Displ`]], Sequence[`Datatype`]]
* Tuple[`Bottom`, Sequence[`Count`], Sequence[`Displ`], Sequence[`Datatype`]]
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
