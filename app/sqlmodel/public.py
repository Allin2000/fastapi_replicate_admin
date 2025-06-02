from tortoise import models, fields

from tortoise.fields import DatetimeField

from datetime import datetime
from tortoise.fields import Field
from tortoise.models import Model
from tortoise.exceptions import ConfigurationError
from typing import Any

class NaiveDatetimeField(Field[datetime], datetime):
    """
    一个自定义的 DatetimeField，它强制创建 TIMESTAMP WITHOUT TIME ZONE 列。
    并始终使用 naive datetime（无时区），不做任何时区转换。
    """

    SQL_TYPE = "TIMESTAMP"  # PostgreSQL 默认 TIMESTAMP 为 WITHOUT TIME ZONE

    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs: Any) -> None:
        if auto_now and auto_now_add:
            raise ConfigurationError("Cannot set both 'auto_now' and 'auto_now_add'")
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now or auto_now_add

    def to_python_value(self, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=None)
        from tortoise.utils import parse_datetime
        return parse_datetime(value).replace(tzinfo=None)

    def to_db_value(self, value: datetime | None, instance: type[Model] | Model) -> datetime | None:
        if hasattr(instance, "_saved_in_db") and (
            self.auto_now or (self.auto_now_add and getattr(instance, self.model_field_name) is None)
        ):
            now = datetime.utcnow()
            setattr(instance, self.model_field_name, now)
            return now

        if isinstance(value, datetime):
            return value.replace(tzinfo=None)

        self.validate(value)
        return value

    @property
    def constraints(self) -> dict:
        return {"readOnly": self.auto_now_add}

    def describe(self, serializable: bool) -> dict:
        desc = super().describe(serializable)
        desc.update({
            "auto_now": self.auto_now,
            "auto_now_add": self.auto_now_add,
        })
        return desc
    

    
# 用户表
class PublicUser(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)
    bio = fields.TextField(null=True)
    image_url = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField()
    updated_at = fields.DatetimeField(null=True)

    class Meta:
        table = "user"
        schema = "public"
        app = "app_public"


class Article(models.Model):
    id = fields.IntField(pk=True)
    slug = fields.CharField(max_length=255, unique=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    body = fields.TextField()
    created_at = NaiveDatetimeField()
    # updated_at = fields.DatetimeField(use_tz=False,null=True)
    updated_at = NaiveDatetimeField(description="更新时间")
    # 修复：使用正确的模型引用格式
    author = fields.ForeignKeyField(
        "app_public.PublicUser", related_name="articles", on_delete=fields.CASCADE
    )

    class Meta:
        table = "article"
        schema = "public"
        app = "app_public"


class Tag(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

    class Meta:
        table = "tag"
        schema = "public"
        app = "app_public"


class ArticleTag(models.Model):
    id = fields.IntField(pk=True)
    # 修复：使用正确的模型引用格式
    article = fields.ForeignKeyField("app_public.Article", related_name="article_tags")
    tag = fields.ForeignKeyField("app_public.Tag", related_name="tag_articles")

    class Meta:
        table = "article_tag"
        schema = "public"
        app = "app_public"


class Comment(models.Model):
    id = fields.IntField(pk=True)
    body = fields.TextField()
    created_at = fields.DatetimeField()
    updated_at = fields.DatetimeField(null=True)
    # 修复：使用正确的模型引用格式
    author = fields.ForeignKeyField("app_public.PublicUser", related_name="comments")
    article = fields.ForeignKeyField("app_public.Article", related_name="comments")

    class Meta:
        table = "comment"
        schema = "public"
        app = "app_public"


class Follow(models.Model):
    id = fields.IntField(pk=True)
    # 修复：使用正确的模型引用格式
    follower = fields.ForeignKeyField("app_public.PublicUser", related_name="following")
    followed = fields.ForeignKeyField("app_public.PublicUser", related_name="followers")

    class Meta:
        table = "follow"
        schema = "public"
        unique_together = (("follower", "followed"),)
        app = "app_public"


class Favorite(models.Model):
    id = fields.IntField(pk=True)
    # 修复：使用正确的模型引用格式
    user = fields.ForeignKeyField("app_public.PublicUser", related_name="favorites")
    article = fields.ForeignKeyField("app_public.Article", related_name="favorited_by")

    class Meta:
        table = "favorite"
        schema = "public"
        unique_together = (("user", "article"),)
        app = "app_public"