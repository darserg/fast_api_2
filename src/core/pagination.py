from dataclasses import dataclass

from fastapi import Query


@dataclass(slots=True)
class PaginationParams:
    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


def get_pagination_params(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
) -> PaginationParams:
    return PaginationParams(page=page, size=size)
