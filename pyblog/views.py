from django.shortcuts import render
from django.views import generic
from .settings import PAGESIZE
from . import models, mixin, form
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime


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
        context['uuid'] = self.kwargs.get('slug')
        return context

    def get_comments(self):
        """
        self.object queryset查询到的结果对象
        :return:
        """
        from django.core.paginator import Paginator
        one_level_comments = self.object.comments.filter(parent__isnull=True).all().order_by('-create_date')[:10]
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


class Comment(mixin.JSONResponseMixin, generic.TemplateView):
    """https://docs.djangoproject.com/en/3.0/topics/class-based-views/mixins/"""
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        article = models.Article(id=kwargs.get('slug'))
        comments = article.comments.all()
        if not comments:
            return JsonResponse(data=[], safe=False)
        return self.render_to_response(context=comments)

    def post(self, request, *args, **kwargs):
        comment_form = form.CommentForm(request.POST)
        context = {
            "code": 0,
            "msg": "",
            "data": {}
        }
        if comment_form.is_valid():
            comment = models.Comment(article=models.Article(id=kwargs.get('slug')),
                                     email=comment_form.cleaned_data['email'],
                                     nick=comment_form.cleaned_data['nick'],
                                     content=comment_form.cleaned_data['content'],
                                     parent=comment_form.cleaned_data['parent_id'],
                                     at=comment_form.cleaned_data['at_id'],
                                     ip=self.request.META['REMOTE_ADDR']
                                     )
            try:
                comment.save()
                context['data'] = {
                    "id": comment.id,
                    "avatar": gravatar(comment.email),
                    "nick": comment.nick,
                    "content": comment.content,
                    "create_date": datetime.strftime(comment.create_date, "%Y/%m/%d %H:%M"),
                }
            except Exception as e:
                print(e)
                context['code'] = 1
        else:
            context['code'] = 1
        return self.render_to_json_response(context=context)

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


def gravatar(email, size=32):
    import hashlib
    return "https://gravatar.com/avatar/%s?s=%s&d=identicon" % (
        hashlib.md5(email.lower().encode()).hexdigest(), str(size))
