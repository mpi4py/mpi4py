from ._base import Future
from typing import Generic, TypeVar, Union
from typing import Callable

_T = TypeVar("_T")

class ThenableFuture(Future[_T], Generic[_T]):
    def then(self,
        on_success: Callable[[_T], Union[_T, Future[_T]]] | None = None,
        on_failure: Callable[[BaseException], Union[_T, BaseException]] | None = None,
    ) -> ThenableFuture[_T]: ...
    def catch(self,
        on_failure: Callable[[BaseException], Union[_T, BaseException]] | None = None,
    ) -> ThenableFuture[_T]: ...

def then(future: Future[_T],
    on_success: Callable[[_T], Union[_T, Future[_T]]] | None = None,
    on_failure: Callable[[BaseException], Union[_T, BaseException]] | None = None,
) -> Future[_T]: ...

def catch(future: Future[_T],
    on_failure: Callable[[BaseException], Union[_T, BaseException]] | None = None,
) -> Future[_T]: ...
