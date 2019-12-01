from django.contrib import admin
from .models import (Article, Tag, Category, Comment,)
from django.db import models
from editormd.widget import TextInputMarkdown
from .form import ArticleAdminForm


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # https://timonweb.com/posts/override-field-widget-in-django-admin-form/
    form = ArticleAdminForm


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

