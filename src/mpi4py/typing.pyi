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

__all__: List[str] = ...

Buffer = Any

Bottom = Union[BottomType, None]

InPlace = Union[InPlaceType, None]

Aint = Integral

Count = Integral

Displ = Integral

Offset = Integral

TypeSpec = Union[Datatype, str]

BufSpec = Union[
    Buffer,
    Tuple[Buffer, Count],
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Count, TypeSpec],
    Tuple[Bottom, Count, Datatype],
    List,
]

BufSpecB = Union[
    Buffer,
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Count, TypeSpec],
    List,
]

BufSpecV = Union[
    Buffer,
    Tuple[Buffer, Count],
    Tuple[Buffer, Tuple[Count, Displ]],
    Tuple[Buffer, TypeSpec],
    Tuple[Buffer, Count, TypeSpec],
    Tuple[Buffer, Tuple[Count, Displ], TypeSpec],
    Tuple[Buffer, Count, Displ, TypeSpec],
    List,
]

BufSpecW = Union[
    Tuple[Buffer, Sequence[Datatype]],
    Tuple[Buffer, Tuple[Sequence[Count], Sequence[Displ]], Sequence[Datatype]],
    Tuple[Buffer, Sequence[Count], Sequence[Displ], Sequence[Datatype]],
    List,
]

TargetSpec = Union[
    Displ,
    Tuple[()],
    Tuple[Displ],
    Tuple[Displ, Count],
    Tuple[Displ, Count, TypeSpec],
    List,
]
