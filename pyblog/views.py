from django.shortcuts import render
from django.views import generic
from .settings import PAGESIZE
from . import models, mixin, form
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core import serializers
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
    ordering = '-pub_date'

    def get_queryset(self):
        content = super().get_queryset().values("id", "title", "pub_date").filter(is_pub=True)
        return content

    def get_context_data(self, *, object_list=None, **kwargs):
        return super().get_context_data(**kwargs)


class Comment(mixin.JSONResponseMixin, generic.TemplateView):
    """https://docs.djangoproject.com/en/3.0/topics/class-based-views/mixins/"""
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        from django.core.paginator import Paginator, QuerySetPaginator
        page = request.GET.get('page', 2) if str(request.GET.get('page', 2)).isdigit() else 2
        size = request.GET.get('size', 10) if str(request.GET.get('size', 10)).isdigit() else 10

        # 设置size上限
        if int(size) > 50:
            size = 10

        context = {
            "code": 0,
            "msg": "",
            "data": {
                "has_next": False,
                "list": []
            }
        }
        article = models.Article(id=kwargs.get('slug'))
        # https://docs.djangoproject.com/en/3.0/topics/pagination/
        paginator = Paginator(article.comments.all().order_by('-create_date'), int(size))

        comments = paginator.get_page(int(page))
        if not comments:
            return self.render_to_response(context=context)
        context['data'] = {
            'has_next': comments.has_next(),
            'list': self.queryset_list_to_json(comments.object_list) if int(page) <= paginator.num_pages else [],
        }
        return self.render_to_response(context=context)

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

    def queryset_list_to_json(self, queryset):
        data = []
        for q in queryset:
            data.append(self.model_to_json(q))
        return data

    @staticmethod
    def model_to_json(obj=models.Comment):
        dic = {}
        exclude = ('ip', 'article_id')
        for key, value in obj.__dict__.items():
            if str(key).startswith('_') or key in exclude:
                continue
            elif isinstance(value, datetime):
                dic.setdefault(key, datetime.strftime(value, '%Y/%m/%d %H:%M'))
            elif key == 'email':
                dic.setdefault('avatar', gravatar(value))
            else:
                dic.setdefault(key, value)
        return dic


class Tag(generic.ListView):
    template_name = 'tag.html'
    context_object_name = 'articles'
    paginate_by = 10
    models = models.Article
    ordering = '-pub_date'

    def get_queryset(self):
        content = models.Article.objects.filter(tags__name=self.kwargs.get('name'), is_pub=True).all()
        return content


def gravatar(email, size=32):
    import hashlib
    from .settings import AVATAR_DOMAIN
    return "%s/avatar/%s?s=%s&d=retro" % (AVATAR_DOMAIN,
                                          hashlib.md5(email.lower().encode()).hexdigest(), str(size))
