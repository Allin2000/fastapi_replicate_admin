from datetime import datetime

from fastapi import APIRouter, Depends, Query
from tortoise.expressions import Q

from app.core.ctx import CTX_USER_ID
from app.services.user import user_controller
from app.services.article import article_controller
from app.sqlmodel.admin import Role
from app.schemas.base import Success, SuccessExtra
from app.schemas.article import ArticleSearch, ArticleUpdate
from app.core.utils import model_to_dict

router = APIRouter()


@router.get("/articles", summary="查看文章列表")
async def get_articles(query: ArticleSearch = Depends()):
    q = Q()

    if query.title:
        q &= Q(title__contains=query.title)
    if query.description:
        q &= Q(description__contains=query.description)
    if query.body:
        q &= Q(body__contains=query.body)
    if query.author_name:
        author = await user_controller.get_by_username(user_name=query.author_name)
        if author:
            q &= Q(author_id=author.id)
    if query.time_range:
        start_ts, end_ts = map(lambda x: int(x) / 1000, query.time_range.split(","))
        q &= Q(create_time__gte=datetime.fromtimestamp(start_ts),
               create_time__lte=datetime.fromtimestamp(end_ts))

    if query.current is None:
        query.current = 1
    if query.size is None:
        query.size = 10

    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get(id=user_id)
    user_roles: list[Role] = await user_obj.roles
    role_codes = [r.role_code for r in user_roles]

    if "R_SUPER" not in role_codes and "R_ADMIN" not in role_codes:
        # 非管理员只能查看自己写的文章
        q &= Q(author_id=user_id)

    total, articles = await article_controller.list(
        page=query.current,
        page_size=query.size,
        search=q,
        order=["-id"]
    )

    records = []
    for article in articles:
        data = await model_to_dict(article, exclude_fields=["author_id"])
        author = await article.author  # type: ignore
        data["authorName"] = author.username if author else "Unknown"
        records.append(data)

    return SuccessExtra(data={"records": records}, total=total, current=query.current, size=query.size)


@router.get("/articles/{article_id}", summary="查看文章详情")
async def get_article_by_id(article_id: int):
    article = await article_controller.get(id=article_id)
    data = await model_to_dict(article, exclude_fields=["author_id"])
    author = await article.author  # type: ignore
    data["authorName"] = author.username if author else "Unknown"
    return Success(data=data)


@router.patch("/articles/{article_id}", summary="更新文章")
async def update_article_by_id(article_id: int, article_in: ArticleUpdate):
    await article_controller.update(id=article_id, obj_in=article_in)
    return Success(msg="Update Successfully")


@router.delete("/articles/{article_id}", summary="删除文章")
async def delete_article_by_id(article_id: int):
    await article_controller.remove(id=article_id)
    return Success(msg="Deleted Successfully", data={"deleted_id": article_id})


@router.delete("/articles", summary="批量删除文章")
async def delete_articles(ids: str = Query(..., description="文章ID列表, 用逗号隔开")):
    article_ids = ids.split(",")
    deleted_ids = []
    for article_id in article_ids:
        article = await article_controller.get(id=int(article_id))
        await article.delete()
        deleted_ids.append(int(article_id))
    return Success(msg="Deleted Successfully", data={"deleted_ids": deleted_ids})