# ruff: noqa: UP007
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

__all__: list[str] = [
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
    if sys.version_info >= (3, 12):
        def __buffer__(self, flags: int, /) -> memoryview: ...

class SupportsDLPack(Protocol):
    def __dlpack__(
        self, /, *, stream: _Stream | None = None
    ) -> _PyCapsule: ...
    def __dlpack_device__(
        self,
    ) -> tuple[_DeviceType, _DeviceID]: ...

class SupportsCAI(Protocol):
    @property
    def __cuda_array_interface__(self) -> dict[str, Any]: ...

Buffer: TypeAlias = Union[
    SupportsBuffer,
    SupportsDLPack,
    SupportsCAI,
]

Bottom: TypeAlias = Union[BottomType, None]

InPlace: TypeAlias = Union[InPlaceType, None]

Aint: TypeAlias = SupportsIndex

Count: TypeAlias = SupportsIndex

Displ: TypeAlias = SupportsIndex

Offset: TypeAlias = SupportsIndex

TypeSpec: TypeAlias = Union[Datatype, str]

BufSpec: TypeAlias = Union[
    Buffer,
    tuple[Buffer, Count],
    tuple[Buffer, TypeSpec],
    tuple[Buffer, Count, TypeSpec],
    tuple[Bottom, Count, Datatype],
    list[Any],
]

BufSpecB: TypeAlias = Union[
    Buffer,
    tuple[Buffer, Count],
    tuple[Buffer, TypeSpec],
    tuple[Buffer, Count, TypeSpec],
    list[Any],
]

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

BufSpecW: TypeAlias = Union[
    tuple[Buffer, Sequence[Datatype]],
    tuple[Buffer, tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    tuple[Buffer, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    tuple[Bottom, tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    tuple[Bottom, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    list[Any],
]

TargetSpec: TypeAlias = Union[
    Displ,
    tuple[()],
    tuple[Displ],
    tuple[Displ, Count],
    tuple[Displ, Count, TypeSpec],
    list[Any],
]

S = TypeVar("S")  # noqa: PYI001
T = TypeVar("T")  # noqa: PYI001
U = TypeVar("U")  # noqa: PYI001
V = TypeVar("V")  # noqa: PYI001
