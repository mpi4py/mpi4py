import sys
from typing import (
    Any,
    Union,
    Optional,
    Protocol,
    Sequence,
    SupportsIndex,
    List,
    Dict,
    Tuple,
    TypeVar,
)
if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias
from .MPI import (
    Datatype,
    BottomType,
    InPlaceType,
)

__all__: List[str] = [
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

_Stream: TypeAlias = Union[int, Any]
_PyCapsule: TypeAlias = object
_DeviceType: TypeAlias = int
_DeviceID: TypeAlias = int

class SupportsBuffer(Protocol):
    if sys.version_info >= (3, 12):
        def __buffer__(self, flags: int, /) -> memoryview: ...

class SupportsDLPack(Protocol):
    def __dlpack__(self, *, stream: Optional[_Stream] = None) -> _PyCapsule: ...
    def __dlpack_device__(self) -> Tuple[_DeviceType, _DeviceID]: ...

class SupportsCAI(Protocol):
    @property
    def __cuda_array_interface__(self) -> Dict[str, Any]: ...

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
    Tuple[Buffer, Count],
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Count, TypeSpec],
    Tuple[Bottom, Count, Datatype],
    List[Any],
]

BufSpecB: TypeAlias = Union[
    Buffer,
    Tuple[Buffer, Count],
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Count, TypeSpec],
    List[Any],
]

BufSpecV: TypeAlias = Union[
    Buffer,
    Tuple[Buffer, Sequence[Count]],
    Tuple[Buffer, Tuple[Sequence[Count], Sequence[Displ]]],
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Sequence[Count], TypeSpec],
    Tuple[Buffer, Tuple[Sequence[Count], Sequence[Displ]], TypeSpec],
    Tuple[Buffer, Sequence[Count], Sequence[Displ], TypeSpec],
    Tuple[Bottom, Tuple[Sequence[Count], Sequence[Displ]], Datatype],
    Tuple[Bottom, Sequence[Count], Sequence[Displ], Datatype],
    List[Any],
]

BufSpecW: TypeAlias = Union[
    Tuple[Buffer, Sequence[Datatype]],
    Tuple[Buffer, Tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    Tuple[Buffer, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    Tuple[Bottom, Tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    Tuple[Bottom, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    List[Any],
]

TargetSpec: TypeAlias = Union[
    Displ,
    Tuple[()],
    Tuple[Displ],
    Tuple[Displ, Count],
    Tuple[Displ, Count, TypeSpec],
    List[Any],
]

S = TypeVar('S')  # noqa: PYI001
T = TypeVar('T')  # noqa: PYI001
U = TypeVar('U')  # noqa: PYI001
V = TypeVar('V')  # noqa: PYI001
