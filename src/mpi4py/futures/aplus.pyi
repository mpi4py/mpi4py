from typing import Generic, TypeVar
from typing import Callable
from ._base import Future

_T = TypeVar("_T")

class ThenableFuture(Future[_T], Generic[_T]):
    def then(self,
        on_success: Callable[[_T], _T | Future[_T]] | None = None,
        on_failure: Callable[[BaseException], _T | BaseException] | None = None,
    ) -> ThenableFuture[_T]: ...
    def catch(self,
        on_failure: Callable[[BaseException], _T | BaseException] | None = None,
    ) -> ThenableFuture[_T]: ...

def then(future: Future[_T],
    on_success: Callable[[_T], _T | Future[_T]] | None = None,
    on_failure: Callable[[BaseException], _T | BaseException] | None = None,
) -> Future[_T]: ...

def catch(future: Future[_T],
    on_failure: Callable[[BaseException], _T | BaseException] | None = None,
) -> Future[_T]: ...
