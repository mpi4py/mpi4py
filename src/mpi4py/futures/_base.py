# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

# pylint: disable=unused-import
# pylint: disable=redefined-builtin
# pylint: disable=missing-module-docstring

from concurrent.futures import (  # noqa: F401
    FIRST_COMPLETED,
    FIRST_EXCEPTION,
    ALL_COMPLETED,
    CancelledError,
    TimeoutError,  # noqa: A004
    BrokenExecutor,
    InvalidStateError,
    Future,
    Executor,
    wait,
    as_completed,
)
