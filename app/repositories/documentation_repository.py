from sqlalchemy import select

from app.models import DocumentationArticle
from app.repositories.base import BaseRepository


class DocumentationRepository(BaseRepository[DocumentationArticle]):
    model_class = DocumentationArticle

    async def search_by_product_area(
        self, area: str, limit: int = 5
    ) -> list[DocumentationArticle]:
        query = (
            select(DocumentationArticle)
            .where(DocumentationArticle.product_area.ilike(f"%{area}%"))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
