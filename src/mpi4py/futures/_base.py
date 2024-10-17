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
    TimeoutError,
    Future,
    Executor,
    wait,
    as_completed,
)

import sys

if sys.version_info >= (3, 7):  # Python 3.7
    from concurrent.futures import BrokenExecutor
else:  # pragma: no cover
    class BrokenExecutor(RuntimeError):
        """The executor has become non-functional."""

if sys.version_info >= (3, 8):  # Python 3.8
    from concurrent.futures import InvalidStateError
else:  # pragma: no cover
    # pylint: disable=too-few-public-methods
    # pylint: disable=useless-object-inheritance
    class InvalidStateError(CancelledError.__base__):
        """The operation is not allowed in this state."""

del sys
