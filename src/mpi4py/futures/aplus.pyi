from typing import Generic
from typing import Callable
from typing import overload
from ._base import Future
from ..typing import S, T, U

class ThenableFuture(Future[T], Generic[T]):
    def then(self,
        on_success: Callable[[T], T | Future[T]] | None = None,
        on_failure: Callable[[BaseException], T | BaseException] | None = None,
    ) -> ThenableFuture[T]: ...
    def catch(self,
        on_failure: Callable[[BaseException], T | BaseException] | None = None,
    ) -> ThenableFuture[T]: ...

@overload
def then(
    future: Future[T],
    on_success: None = None,
    on_failure: None = None,
) -> Future[T]: ...

@overload
def then(
    future: Future[T],
    on_success: Callable[[T], S | Future[S]],
    on_failure: None = None,
) -> Future[S]: ...

@overload
def then(
    future: Future[T],
    on_success: None = None, *,
    on_failure: Callable[[BaseException], BaseException | U | Future[U]],
) -> Future[T | U]: ...

@overload
def then(
    future: Future[T],
    on_success: Callable[[T], S | Future[S]],
    on_failure: Callable[[BaseException], BaseException | U | Future[U]],
) -> Future[S | U]: ...

@overload
def catch(
    future: Future[T],
    on_failure: None = None,
) -> Future[T]: ...

@overload
def catch(
    future: Future[T],
    on_failure: Callable[[BaseException], BaseException | U | Future[U]],
) -> Future[T | U]: ...
