from app.services.crud import CRUDBase
from app.sqlmodel.public import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


class ArticleController(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    def __init__(self):
        super().__init__(model=Article)


article_controller = ArticleController()