from django.shortcuts import render
from django.views import generic
from django.db.models import Count, Q
from .settings import PAGESIZE
from . import models, mixin, form
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from pyblog .templatetags.pyblog import gravatar


def handler404(request, exception=None):
    return render(request, '404.html', {}, status=404)


class Index(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'articles'
    model = models.Article
    paginate_by = PAGESIZE

    def get_queryset(self):
        content = models.Article.objects.annotate(
             num_comment=Count('comments', filter=Q(comments__parent__isnull=True))). \
            filter(is_pub=True).all().order_by('-pub_date')
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
        return query.annotate(num_comment=Count('comments',
                                                filter=Q(comments__parent__isnull=True))).filter(is_pub=True)

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
        from django.db.models import Count
        comments = {"count": 0, "data": []}
        comment_count = self.object.comments.filter(parent__isnull=True).aggregate(Count('id')).get("id__count", 0)
        comments.update({
            "count": comment_count,
        })
        one_level_comments = self.object.comments.filter(
            parent__isnull=True).all().order_by(
            '-create_date')[0:comment_count if (comment_count-10) < 0 else comment_count-10]
        for c in one_level_comments:
            comments.get("data").append(
                dict(c.__dict__, **{"reply": [Comment.model_to_json(r) for r in c.get_two_level_comments(c.id)]}))
        return comments


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
        _count = request.GET.get('count', 0) if str(request.GET.get('count', 0)).isdigit() else 0
        article_id = self.kwargs.get("slug")

        if int(page) <= 0:
            page = 1
        page = int(page)
        # 设置size上限
        if int(size) > 50:
            size = 10
        size = int(size)
        """
        反向分页, 如: 数据库查询的数据,按时间升序。前端获取的数据是降序，即第一条应该是最新的。
        如果使用降序分页查询，此时如果数据库又有新数据，会导致下一页可能包含上一页的重复数据。
        逆向思维:
            数据库按时间升序查询，分页反向。
            假设数据库有15条数据，每页为5条。
            1.按降序查询的话，最新的5条数据应该是第一页。
            2.按升序查询的话，最新的5条数据应该是第三页。
        """
        import math
        page_count = math.ceil(int(_count) / int(size))
        m = page_count + 1
        page = m - int(page)

        context = {
            "code": 0,
            "msg": "",
            "data": {
                "has_next": False,
                "list": []
            }
        }
        if page < 1:
            return self.render_to_response(context=context)
        article = models.Article(id=kwargs.get('slug'))
        # https://docs.djangoproject.com/en/3.0/topics/pagination/
        paginator = Paginator(article.comments.filter(article_id=article_id,
                                                      parent__isnull=True).all().order_by('create_date'), int(size))

        comments = paginator.get_page(int(page_count - page))
        if not comments:
            return self.render_to_response(context=context)
        context['data'] = {
            'has_next': comments.has_next() if comments.object_list.__len__() > size else False,
            'list': self.queryset_list_to_json(comments.object_list)[::-1] if int(page) <= paginator.num_pages else [],
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
                                     parent_id=comment_form.cleaned_data['parent_id'],
                                     at_id=comment_form.cleaned_data['at_id'],
                                     ip=self.request.META['REMOTE_ADDR']
                                     )
            try:
                comment.save()
                context['data'] = {
                    "id": comment.id,
                    "avatar": gravatar(comment.email),
                    "nick": comment.nick,
                    "content": comment.content,
                    "parent_id": comment.parent_id,
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
            reply = [self.model_to_json(r) for r in q.get_two_level_comments(q.id)]
            data.append(dict(self.model_to_json(q), **{"reply": reply}))
        return data

    @staticmethod
    def model_to_json(obj=models.Comment):
        dic = {}
        exclude = ('ip', 'article_id')
        items = {}
        if isinstance(obj, dict):
            items = obj.items()
        elif isinstance(obj, models.Comment):
            items = obj.__dict__.items()
        else:
            return dic
        for key, value in items:
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


class AboutMe(generic.DetailView):
    template_name = 'about.html'
    context_object_name = 'about_me'
    model = models.Info
    # queryset = model.objects.all()

    # 重写该函数,可以不指定slug
    def get_object(self, queryset=None):
        try:
            about_me = self.model.objects.get(i_type=self.model.INFO_TYPE_CHOICES[0][0], is_pub=True)
        except models.Info.DoesNotExist:
            return models.Info(content="""*博主太懒,没有自我介绍*
            """)
        return about_me


class Coffee(generic.DetailView):
    template_name = 'coffee.html'
    context_object_name = 'coffee'
    model = models.Info

    # 重写该函数,可以不指定slug
    def get_object(self, queryset=None):
        try:
            coffee = self.model.objects.get(i_type=self.model.INFO_TYPE_CHOICES[1][0], is_pub=True)
        except models.Info.DoesNotExist:
            return models.Info(content="""*欢迎访问我的网站 ^_^*
            """)
        return coffee
