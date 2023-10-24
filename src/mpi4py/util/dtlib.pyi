from typing import Any
from numpy import dtype
from numpy.typing import DTypeLike
from ..MPI import Datatype

def from_numpy_dtype(dtype: DTypeLike) -> Datatype: ...
def to_numpy_dtype(datatype: Datatype) -> dtype[Any]: ...
