# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Typing support."""
# pylint: disable=too-few-public-methods

import sys
from collections.abc import (
    Sequence,
)
from typing import (
    Any,
    Protocol,
    SupportsIndex,
    TypeAlias,
    TypeVar,
    Union,
)

from .MPI import (
    BottomType,
    Datatype,
    InPlaceType,
)

__all__ = [
    "SupportsBuffer",
    "SupportsDLPack",
    "SupportsCAI",
    "Buffer",
    "Bottom",
    "InPlace",
    "Aint",
    "Count",
    "Displ",
    "Offset",
    "TypeSpec",
    "BufSpec",
    "BufSpecB",
    "BufSpecV",
    "BufSpecW",
    "TargetSpec",
]

_Stream: TypeAlias = Union[int, Any]
_PyCapsule: TypeAlias = object
_DeviceType: TypeAlias = int
_DeviceID: TypeAlias = int


class SupportsBuffer(Protocol):
    """Python buffer protocol.

    .. seealso:: :ref:`python:bufferobjects`
    """

    if sys.version_info >= (3, 12):  # pragma: no branch

        def __buffer__(self, flags: int, /) -> memoryview:
            """Create a buffer from a Python object."""


class SupportsDLPack(Protocol):
    """DLPack data interchange protocol.

    .. seealso:: :ref:`dlpack:python-spec`
    """

    def __dlpack__(self, /, *, stream: _Stream | None = None) -> _PyCapsule:
        """Export data for consumption as a DLPack capsule."""

    def __dlpack_device__(self) -> tuple[_DeviceType, _DeviceID]:
        """Get device type and device ID in DLPack format."""


class SupportsCAI(Protocol):
    """CUDA Array Interface (CAI) protocol.

    .. seealso:: :ref:`numba:cuda-array-interface`
    """

    @property
    def __cuda_array_interface__(self) -> dict[str, Any]:
        """CAI protocol data."""


Buffer: TypeAlias = Union[
    SupportsBuffer,
    SupportsDLPack,
    SupportsCAI,
]
"""
Buffer-like object.
"""


Bottom: TypeAlias = Union[BottomType, None]
"""
Start of the address range.
"""


InPlace: TypeAlias = Union[InPlaceType, None]
"""
In-place buffer argument.
"""


Aint: TypeAlias = SupportsIndex
"""
Address-sized integral type.
"""


Count: TypeAlias = SupportsIndex
"""
Integral type for counts.
"""


Displ: TypeAlias = SupportsIndex
"""
Integral type for displacements.
"""


Offset: TypeAlias = SupportsIndex
"""
Integral type for offsets.
"""


TypeSpec: TypeAlias = Union[Datatype, str]
"""
Datatype specification.
"""


BufSpec: TypeAlias = Union[
    Buffer,
    tuple[Buffer, Count],
    tuple[Buffer, TypeSpec],
    tuple[Buffer, Count, TypeSpec],
    tuple[Bottom, Count, Datatype],
    list[Any],
]
"""
Buffer specification.

* `Buffer`
* tuple[`Buffer`, `Count`]
* tuple[`Buffer`, `TypeSpec`]
* tuple[`Buffer`, `Count`, `TypeSpec`]
* tuple[`Bottom`, `Count`, `Datatype`]
"""


BufSpecB: TypeAlias = Union[
    Buffer,
    tuple[Buffer, Count],
    tuple[Buffer, TypeSpec],
    tuple[Buffer, Count, TypeSpec],
    list[Any],
]
"""
Buffer specification (block).

* `Buffer`
* tuple[`Buffer`, `Count`]
* tuple[`Buffer`, `TypeSpec`]
* tuple[`Buffer`, `Count`, `TypeSpec`]
"""


BufSpecV: TypeAlias = Union[
    Buffer,
    tuple[Buffer, Sequence[Count]],
    tuple[Buffer, tuple[Sequence[Count], Sequence[Displ]]],
    tuple[Buffer, TypeSpec],
    tuple[Buffer, Sequence[Count], TypeSpec],
    tuple[Buffer, tuple[Sequence[Count], Sequence[Displ]], TypeSpec],
    tuple[Buffer, Sequence[Count], Sequence[Displ], TypeSpec],
    tuple[Bottom, tuple[Sequence[Count], Sequence[Displ]], Datatype],
    tuple[Bottom, Sequence[Count], Sequence[Displ], Datatype],
    list[Any],
]
"""
Buffer specification (vector).

* `Buffer`
* tuple[`Buffer`, Sequence[`Count`]]
* tuple[`Buffer`, tuple[Sequence[`Count`], Sequence[`Displ`]]]
* tuple[`Buffer`, `TypeSpec`]
* tuple[`Buffer`, Sequence[`Count`], `TypeSpec`]
* tuple[`Buffer`, tuple[Sequence[`Count`], Sequence[`Displ`]], `TypeSpec`]
* tuple[`Buffer`, Sequence[`Count`], Sequence[`Displ`], `TypeSpec`]
* tuple[`Bottom`, tuple[Sequence[`Count`], Sequence[`Displ`]], `Datatype`]
* tuple[`Bottom`, Sequence[`Count`], Sequence[`Displ`], `Datatype`]
"""


BufSpecW: TypeAlias = Union[
    tuple[Buffer, Sequence[Datatype]],
    tuple[Buffer, tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    tuple[Buffer, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    tuple[Bottom, tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    tuple[Bottom, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    list[Any],
]
"""
Buffer specification (generalized).

* tuple[`Buffer`, Sequence[`Datatype`]]
* tuple[`Buffer`, \
          tuple[Sequence[`Count`], Sequence[`Displ`]], Sequence[`Datatype`]]
* tuple[`Buffer`, Sequence[`Count`], Sequence[`Displ`], Sequence[`Datatype`]]
* tuple[`Bottom`, \
          tuple[Sequence[`Count`], Sequence[`Displ`]], Sequence[`Datatype`]]
* tuple[`Bottom`, Sequence[`Count`], Sequence[`Displ`], Sequence[`Datatype`]]
"""


TargetSpec: TypeAlias = Union[
    Displ,
    tuple[()],
    tuple[Displ],
    tuple[Displ, Count],
    tuple[Displ, Count, TypeSpec],
    list[Any],
]
"""
Target specification.

* `Displ`
* tuple[()]
* tuple[`Displ`]
* tuple[`Displ`, `Count`]
* tuple[`Displ`, `Count`, `TypeSpec`]
"""


S = TypeVar("S")
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
