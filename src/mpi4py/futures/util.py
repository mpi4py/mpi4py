# Author:  Lisandro Dalcin
# Contact: dalcinl@gmail.com
"""Utilities for handling futures."""
# pylint: disable=too-few-public-methods
# pylint: disable=broad-exception-caught

import collections as _collections
import functools as _functools
import threading as _threading

from . import _base

__all__ = [
    "collect",
    "compose",
]


def collect(fs):
    """Gather a collection of futures in a new future.

    Args:
        fs: Collection of futures.

    Returns:
        New future producing as result a list with results from *fs*.

    """
    return _Collect()(fs)


class _Collect:
    #
    def __init__(self):
        self.lock = _threading.RLock()
        self.future = None
        self.result = None
        self.pending = None

    def __call__(self, fs):
        pending = _collections.defaultdict(list)
        for index, item in enumerate(fs):
            pending[item].append(index)
        if pending:
            self.future = future = next(iter(pending)).__class__()
            self.result = [None] * sum(map(len, pending.values()))
            self.pending = pending
            future.add_done_callback(self._done_cb)
            for item in list(pending):
                item.add_done_callback(self._item_cb)
        else:
            future = _base.Future()
            future.set_result([])
        return future

    def _item_cb(self, item):
        with self.lock:
            future = self.future
            result = self.result
            pending = self.pending
            if future is None:
                return
            if item.cancelled():
                future.cancel()
                return
            if item.exception() is not None:
                if future.set_running_or_notify_cancel():  # pragma: no branch
                    future.set_exception(item.exception())
                return
            for index in pending.pop(item):
                result[index] = item.result()
            if not pending:
                if future.set_running_or_notify_cancel():  # pragma: no branch
                    future.set_result(result)

    def _done_cb(self, future):
        with self.lock:
            for item in self.pending:
                item.cancel()
            self.future = None
            self.result = None
            self.pending = None
        if future.cancelled():
            future.set_running_or_notify_cancel()


def compose(future, resulthook=None, excepthook=None):
    """Compose the completion of a future with result and exception handlers.

    Args:
        future: Input future instance.
        resulthook: Function to be called once the input future completes with
            success. Once the input future finish running with success, its
            result value is the input argument for *resulthook*. The result of
            *resulthook* is set as the result of the output future.
            If *resulthook* is ``None``, the output future is completed
            directly with the result of the input future.
        excepthook: Function to be called once the input future completes with
            failure. Once the input future finish running with failure, its
            exception value is the input argument for *excepthook*.  If
            *excepthook* returns an `python:Exception` instance, it is set as
            the exception of the output future.  Otherwise, the result of
            *excepthook* is set as the result of the output future.  If
            *excepthook* is ``None``, the output future is set as failed with
            the exception from the input future.

    Returns:
        Output future instance to be completed once the input future is
        completed and either *resulthook* or *excepthook* finish executing.

    """
    new_future = future.__class__()
    new_done_cb = _functools.partial(_compose_cancel, [future])
    new_future.add_done_callback(new_done_cb)
    context = [(new_future, resulthook, excepthook)]
    done_cb = _functools.partial(_compose_complete, context)
    future.add_done_callback(done_cb)
    return new_future


def _compose_cancel(context, new_future):
    old_future = context.pop()
    try:
        if new_future.cancelled():
            new_future.set_running_or_notify_cancel()
            old_future.cancel()
    finally:
        new_future = None
        old_future = None


def _compose_complete(context, old_future):
    new_future, resulthook, excepthook = context.pop()
    try:
        if old_future.cancelled():
            new_future.cancel()
        elif old_future.exception() is not None:
            reason = old_future.exception()
            if excepthook:
                reason = excepthook(reason)
            if isinstance(reason, BaseException):
                new_future.set_exception(reason)
            else:
                new_future.set_result(reason)
        else:
            result = old_future.result()
            if resulthook:
                result = resulthook(result)
            new_future.set_result(result)
    except BaseException as exception:
        new_future.set_exception(exception)
    finally:
        new_future = None
        old_future = None
        result = resulthook = None
        reason = excepthook = None
