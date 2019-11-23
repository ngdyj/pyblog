from django.shortcuts import render
from django.views import generic
from . import models


def index(request):
    return render(request, 'index.html')


class Index(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'articles'
    model = models.Article


class ArticleDetail(generic.DetailView):
    template_name = 'article_detail.html'
    context_object_name = 'detail'
    model = models.Article
    slug_field = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
