from django.shortcuts import render
from django.views import generic


def index(request):
    return render(request, 'index.html')


class Index(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'home_article_list'

    def get_queryset(self):
        return {"test": "aaaaa"}
