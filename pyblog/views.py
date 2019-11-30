from django.shortcuts import render
from django.views import generic
from . import models


def index(request):
    return render(request, 'index.html')


class Index(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'articles'
    model = models.Article

    def get_queryset(self):
        if "category" in self.request.GET:
            category = self.request.GET['category']
            content = models.Article.objects.select_related('category').filter(is_pub=True,
                                                                               category__name=category).all()
        else:
            content = models.Article.objects.all()
        return content

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ArticleDetail(generic.DetailView):
    template_name = 'article_detail.html'
    context_object_name = 'article'
    model = models.Article
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
