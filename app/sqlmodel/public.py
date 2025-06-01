from tortoise import models, fields

from tortoise.fields import DatetimeField

class NaiveDatetimeField(DatetimeField):
    """
    一个自定义的 DatetimeField，它强制在数据库中创建
    TIMESTAMP WITHOUT TIME ZONE 类型的列，以匹配 SQLAlchemy 的默认行为。
    """
    @property
    def SQL_TYPE(self) -> str:
        # 对于 PostgreSQL, "TIMESTAMP" 就是 "TIMESTAMP WITHOUT TIME ZONE"
        return "TIMESTAMP"

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
    created_at = fields.DatetimeField()
    # updated_at = fields.DatetimeField(use_tz=False,null=True)
    updated_at = NaiveDatetimeField(auto_now=True, description="更新时间")
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