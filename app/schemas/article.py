from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ArticleBase(BaseModel):
    slug: str
    title: str
    description: str
    body: str


class ArticleCreate(ArticleBase):
    author_id: int  # 如果你不自动从当前用户推导作者，则需要手动传入


class ArticleUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    body: str | None = None
    updated_at: datetime | None = None



class ArticleSearch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    author_name: Optional[str] = None
    time_range: Optional[str] = None  # 格式为时间戳字符串: "start,end"
    current: Optional[int] = 1
    size: Optional[int] = 10