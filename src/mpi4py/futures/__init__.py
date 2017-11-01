# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Execute computations asynchronously using MPI processes."""
# pylint: disable=redefined-builtin

try:
    from concurrent.futures import (
        FIRST_COMPLETED,
        FIRST_EXCEPTION,
        ALL_COMPLETED,
        CancelledError,
        TimeoutError,
        Future,
        Executor,
        wait,
        as_completed,
    )
except ImportError:  # pragma: no cover
    from ._base import (
        FIRST_COMPLETED,
        FIRST_EXCEPTION,
        ALL_COMPLETED,
        CancelledError,
        TimeoutError,
        Future,
        Executor,
        wait,
        as_completed,
    )

from .pool import MPIPoolExecutor
from .pool import MPICommExecutor

from .pool import ThreadPoolExecutor
from .pool import ProcessPoolExecutor
