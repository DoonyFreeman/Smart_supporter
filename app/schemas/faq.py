from datetime import datetime

from pydantic import BaseModel, Field


class FAQArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    keywords: str = Field(min_length=1, max_length=500)
    category: str = Field(min_length=1, max_length=100)


class FAQArticleResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    content: str
    keywords: str
    category: str
    created_at: datetime
