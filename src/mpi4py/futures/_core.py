# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com

# pylint: disable=unused-import
# pylint: disable=redefined-builtin
# pylint: disable=missing-module-docstring

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

    try:  # Python 3.7
        from concurrent.futures import BrokenExecutor
    except ImportError:  # pragma: no cover
        BrokenExecutor = RuntimeError

    try:  # Python 3.8
        from concurrent.futures import InvalidStateError
    except ImportError:  # pragma: no cover
        InvalidStateError = CancelledError.__base__

except ImportError:  # pragma: no cover

    from ._base import (
        FIRST_COMPLETED,
        FIRST_EXCEPTION,
        ALL_COMPLETED,
        CancelledError,
        TimeoutError,
        InvalidStateError,
        BrokenExecutor,
        Future,
        Executor,
        wait,
        as_completed,
    )
