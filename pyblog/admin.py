from django.contrib import admin
from .models import (Article, Tag, Category, Comment, Info)
from django.db import models
from editormd.widget import TextInputMarkdown
from .form import ArticleAdminForm, InfoAdminForm


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # https://timonweb.com/posts/override-field-widget-in-django-admin-form/
    form = ArticleAdminForm
    list_display = ('title', 'pub_date')
    ordering = ('-pub_date',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'nick', 'content', 'parent', 'at')
    list_per_page = 20  # 每页几条数据


@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    form = InfoAdminForm
    list_display = ('title', 'pub_date')
    ordering = ('-pub_date',)


