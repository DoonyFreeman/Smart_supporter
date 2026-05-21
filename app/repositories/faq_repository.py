from sqlalchemy import select

from app.models import FAQArticle
from app.repositories.base import BaseRepository


class FAQRepository(BaseRepository[FAQArticle]):
    model_class = FAQArticle

    async def search_by_keywords(
        self, keywords: str, limit: int = 5
    ) -> list[FAQArticle]:
        query = (
            select(FAQArticle)
            .where(FAQArticle.keywords.ilike(f"%{keywords}%"))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
