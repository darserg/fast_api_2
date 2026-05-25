from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: Sequence[T]
    page: int
    size: int
    total: int
