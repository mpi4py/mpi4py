from typing import Generic, TypeVar
from typing import Callable
from typing import overload
from ._base import Future

_T = TypeVar("_T")
_S = TypeVar("_S")
_F = TypeVar("_F")

class ThenableFuture(Future[_T], Generic[_T]):
    def then(self,
        on_success: Callable[[_T], _T | Future[_T]] | None = None,
        on_failure: Callable[[BaseException], _T | BaseException] | None = None,
    ) -> ThenableFuture[_T]: ...
    def catch(self,
        on_failure: Callable[[BaseException], _T | BaseException] | None = None,
    ) -> ThenableFuture[_T]: ...

@overload
def then(
    future: Future[_T],
    on_success: None = None,
    on_failure: None = None,
) -> Future[_T]: ...

@overload
def then(
    future: Future[_T],
    on_success: Callable[[_T], _S | Future[_S]],
    on_failure: None = None,
) -> Future[_S]: ...

@overload
def then(
    future: Future[_T],
    on_success: None = None, *,
    on_failure: Callable[[BaseException], BaseException | _F | Future[_F]],
) -> Future[_T | _F]: ...

@overload
def then(
    future: Future[_T],
    on_success: Callable[[_T], _S | Future[_S]],
    on_failure: Callable[[BaseException], BaseException | _F | Future[_F]],
) -> Future[_S | _F]: ...

@overload
def catch(
    future: Future[_T],
    on_failure: None = None,
) -> Future[_T]: ...

@overload
def catch(
    future: Future[_T],
    on_failure: Callable[[BaseException], BaseException | _F | Future[_F]],
) -> Future[_T | _F]: ...
