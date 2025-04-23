# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Execute computations asynchronously using MPI processes."""
# pylint: disable=redefined-builtin

from ._base import (
    ALL_COMPLETED,
    FIRST_COMPLETED,
    FIRST_EXCEPTION,
    BrokenExecutor,
    CancelledError,
    Executor,
    Future,
    InvalidStateError,
    TimeoutError,  # noqa: A004
    as_completed,
    wait,
)
from .pool import (
    MPICommExecutor,
    MPIPoolExecutor,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
    get_comm_workers,
)
from .util import (
    collect,
    compose,
)

__all__ = [
    "Future",
    "Executor",
    "wait",
    "FIRST_COMPLETED",
    "FIRST_EXCEPTION",
    "ALL_COMPLETED",
    "as_completed",
    "CancelledError",
    "TimeoutError",
    "InvalidStateError",
    "BrokenExecutor",
    "MPIPoolExecutor",
    "MPICommExecutor",
    "ThreadPoolExecutor",
    "ProcessPoolExecutor",
    "get_comm_workers",
    "collect",
    "compose",
]
