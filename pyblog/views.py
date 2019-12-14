from django.shortcuts import render
from django.views import generic
from .settings import PAGESIZE
from . import models


def index(request):
    return render(request, 'index.html')


class Index(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'articles'
    model = models.Article
    paginate_by = PAGESIZE

    def get_queryset(self):
        if "category" in self.request.GET:
            category = self.request.GET['category']
            content = models.Article.objects.select_related('category').filter(is_pub=True,
                                                                               category__name=category).all().order_by('-pub_date')
        else:
            content = models.Article.objects.filter(is_pub=True).all().order_by('-pub_date')
        return content

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ArticleDetail(generic.DetailView):
    template_name = 'article_detail.html'
    context_object_name = 'article'
    model = models.Article
    slug_field = 'id'

    def get_queryset(self):
        query = super().get_queryset()
        return query.filter(is_pub=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.get_comments()
        return context

    def get_comments(self):
        """
        self.object queryset查询到的结果对象
        :return:
        """
        from django.core.paginator import Paginator
        one_level_comments = Paginator(self.object.comments.filter(parent__isnull=True).all()[:10], 1)
        # one_level_comments = self.object.comments.filter(parent__isnull=True).all()[:10]
        return one_level_comments


class Archive(generic.ArchiveIndexView):
    """
    归档
    参考室友代码: https://github.com/zytx/pyblog
    """
    template_name = "archive.html"
    context_object_name = "articles"
    date_field = "pub_date"
    date_list_period = "month"
    model = models.Article

    def get_queryset(self):
        content = super().get_queryset().values("id", "title", "pub_date")
        return content

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(**kwargs)
