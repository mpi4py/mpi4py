# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Support for Future chaining."""
# pylint: disable=broad-exception-caught

# This implementation is heavily inspired in code written by
# Daniel Dotsenko [@dvdotsenko] [dotsa at hotmail.com]
# https://github.com/dvdotsenko/python-future-then

import functools
import threading
import weakref

from ._base import Future


class ThenableFuture(Future):
    """*Thenable* `Future` subclass."""

    def then(self, on_success=None, on_failure=None):
        """Return ``then(self, on_success, on_failure)``."""
        return then(self, on_success, on_failure)

    def catch(self, on_failure=None):
        """Return ``catch(self, on_failure)``."""
        return catch(self, on_failure)


def then(future, on_success=None, on_failure=None):
    """JavaScript-like (`Promises/A+`_) support for Future chaining.

    Args:
        future: Input future instance.
        on_success: Function to be called once the input future completes
            with success. Once the input future finish running with success,
            its result value is the input argument for *on_success*.
            If *on_success* returns a `Future` instance, the result future is
            chained to the output future.  Otherwise, the result of
            *on_success* is set as the result of the output future.
            If *on_success* is ``None``, the output future is resolved directly
            with the result of the input future.
        on_failure: Function to be called once the input future completes with
            failure. Once the input future finish running with failure, its
            exception value is the input argument for *on_failure*.
            If *on_failure* returns a `Future` instance, the result future is
            chained to the output future. Otherwise, if *on_failure* returns an
            `Exception` instance, it is set as the exception of the output
            future.  Otherwise, the result of *on_failure* is set as the result
            of the output future.
            If *on_failure* is ``None``, the output future is set as failed
            with the exception from the input future.

    Returns:
        Output future instance to be completed once the input future is
        completed and either *on_success* or *on_failure* completes.

    .. _Promises/A+: https://promisesaplus.com/

    """
    return _chain(future, on_success, on_failure)


def catch(future, on_failure=None):
    """Close equivalent to ``then(future, None, on_failure)``.

    Args:
        future: Input future instance.
        on_failure: Function to be called once the input future completes with
            failure. Once the input future finish running with failure, its
            exception value is the input argument for *on_failure*.
            If *on_failure* returns a `Future` instance, the result future is
            chained to the output future. Otherwise, if *on_failure* returns an
            `Exception` instance, it is set as the exception of the output
            future.  Otherwise, the result of *on_failure* is set as the result
            of the output future.
            If *on_failure* is ``None``, the output future is set as failed
            with the exception from the input future.

    Returns:
        Output future instance to be completed once the input future is
        completed and *on_failure* completes.

    """
    if on_failure is None:
        return then(future, None, lambda _: None)
    return then(future, None, on_failure)


def _chain(future, on_success=None, on_failure=None):
    new_future = future.__class__()
    done_cb = functools.partial(
        _chain_resolve,
        [new_future],
        on_success=on_success,
        on_failure=on_failure,
    )
    future.add_done_callback(done_cb)
    return new_future


_chain_log_lock = threading.Lock()
_chain_log_registry = weakref.WeakKeyDictionary()


def _chain_check_cycle(new_future, future):
    if new_future is future:
        raise RuntimeError(
            f"chain cycle detected: Future {future} chained with itself"
        )
    with _chain_log_lock:
        registry = _chain_log_registry
        try:
            log = registry[new_future]
        except KeyError:
            log = weakref.WeakSet()
            registry[new_future] = log
        if future in log:
            raise RuntimeError(
                f"chain cycle detected: Future {future} already in chain"
            )
        log.add(future)


def _chain_resolve_future(new_future, old_future):
    _chain_check_cycle(new_future, old_future)
    done_cb = functools.partial(_chain_resolve, [new_future])
    old_future.add_done_callback(done_cb)


def _chain_resolve_success(new_future, result, on_success=None):
    try:
        if on_success:
            result = on_success(result)
        if isinstance(result, Future):
            _chain_resolve_future(new_future, result)
        else:
            new_future.set_result(result)
    finally:
        del new_future, result, on_success


def _chain_resolve_failure(new_future, reason, on_failure=None):
    try:
        if on_failure:
            try:
                reason = on_failure(reason)
                if isinstance(reason, Future):
                    _chain_resolve_future(new_future, reason)
                elif isinstance(reason, BaseException):
                    new_future.set_exception(reason)
                else:
                    new_future.set_result(reason)
            except BaseException as exception:
                new_future.set_exception(exception)
        else:
            new_future.set_exception(reason)
    finally:
        del new_future, reason, on_failure


def _chain_resolve(ctx, old_future, on_success=None, on_failure=None):
    new_future = ctx.pop()
    if old_future.cancelled() or new_future.cancelled():
        new_future.cancel()
        new_future.set_running_or_notify_cancel()
        return
    try:
        if old_future.exception() is not None:
            _chain_resolve_failure(
                new_future,
                old_future.exception(),
                on_failure,
            )
        else:
            try:
                _chain_resolve_success(
                    new_future,
                    old_future.result(),
                    on_success,
                )
            except BaseException as exception:
                _chain_resolve_failure(
                    new_future,
                    exception,
                    on_failure,
                )
    finally:
        del new_future, old_future
