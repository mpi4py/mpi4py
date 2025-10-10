from collections.abc import Sequence

from .MPI import Intracomm

def helloworld(
    comm: Intracomm, args: Sequence[str] | None = None, verbose: bool = True
) -> str: ...
def ringtest(
    comm: Intracomm, args: Sequence[str] | None = None, verbose: bool = True
) -> float: ...
def pingpong(
    comm: Intracomm, args: Sequence[str] | None = None, verbose: bool = True
) -> list[tuple[int, float, float]]: ...
def futures(
    comm: Intracomm, args: Sequence[str] | None = None, verbose: bool = True
) -> list[tuple[int, float, float]]: ...
def main(args: Sequence[str] | None = ...) -> None: ...
