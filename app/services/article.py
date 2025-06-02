# from app.services.crud import CRUDBase
# from app.sqlmodel.public import Article
# from app.schemas.article import ArticleCreate, ArticleUpdate


# class ArticleController(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
#     def __init__(self):
#         super().__init__(model=Article)


# article_controller = ArticleController()


from datetime import datetime,timezone
from typing import Any

from app.services.crud import CRUDBase
from app.sqlmodel.public import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


class ArticleController(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    def __init__(self):
        super().__init__(model=Article)

    async def update(
        self,
        id: int,
        obj_in: ArticleUpdate | dict[str, Any],
        exclude=None,
    ) -> Article:
        if isinstance(obj_in, dict):
            obj_dict = obj_in.copy()
        else:
            obj_dict = obj_in.model_dump(exclude_unset=True, exclude_none=True, exclude=exclude)


        obj = await self.get(id=id)
        obj = obj.update_from_dict(obj_dict)
        obj.updated_at = datetime.now()
        await obj.save()
        return obj


article_controller = ArticleController()