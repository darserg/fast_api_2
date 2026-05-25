from src.repositories.categories import CategoryRepository
from src.repositories.locations import LocationRepository


class CatalogService:
    def __init__(
        self,
        category_repo: CategoryRepository,
        location_repo: LocationRepository,
    ) -> None:
        self.category_repo = category_repo
        self.location_repo = location_repo

    async def list_categories(self):
        return await self.category_repo.get_published()

    async def list_locations(self):
        return await self.location_repo.get_published()

    async def get_category_by_slug(self, slug: str):
        return await self.category_repo.get_by_slug(slug)
