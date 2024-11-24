# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Execute computations asynchronously using MPI processes."""
# pylint: disable=redefined-builtin

from ._base import (
    Future,
    Executor,
    wait,
    FIRST_COMPLETED,
    FIRST_EXCEPTION,
    ALL_COMPLETED,
    as_completed,
    CancelledError,
    TimeoutError,  # noqa: A004
    InvalidStateError,
    BrokenExecutor,
)
from .pool import (
    MPIPoolExecutor,
    MPICommExecutor,
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    get_comm_workers,
)
from .util import (
    collect,
    compose,
)

__all__ = [
    'Future',
    'Executor',
    'wait',
    'FIRST_COMPLETED',
    'FIRST_EXCEPTION',
    'ALL_COMPLETED',
    'as_completed',
    'CancelledError',
    'TimeoutError',
    'InvalidStateError',
    'BrokenExecutor',
    'MPIPoolExecutor',
    'MPICommExecutor',
    'ThreadPoolExecutor',
    'ProcessPoolExecutor',
    'get_comm_workers',
    'collect',
    'compose',
]
