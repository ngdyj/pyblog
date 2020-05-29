from abc import ABC

from django.contrib import admin
from .models import (Article, Tag, Comment, Info)
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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    class CommentInline(admin.TabularInline):
        model = Comment
        fk_name = "parent"
        extra = 0
        ordering = ('create_date',)
        # readonly_fields = ('article', 'at')
        # fields = ['id', 'nick', 'email',  'content', 'article']

    class CommentFilter(admin.SimpleListFilter, ABC):
        title = "一级评论"
        parameter_name = "..."

        def lookups(self, request, model_admin):
            return [
                ('email', 'nick'),
            ]

        def queryset(self, request, queryset):
            return queryset.distinct().filter(parent=None)

    list_display = ('id', 'email', 'nick', 'content', 'article')
    list_per_page = 20  # 每页几条数据
    inlines = [CommentInline]
    list_filter = (CommentFilter,)
    exclude = ["parent", "at"]


@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    form = InfoAdminForm
    list_display = ('title', 'pub_date')
    ordering = ('-pub_date',)


