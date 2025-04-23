# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

# pylint: disable=unused-import
# pylint: disable=redefined-builtin
# pylint: disable=missing-module-docstring

from concurrent.futures import (  # noqa: F401
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
