from django import template
from ..models import Category
import hashlib

register = template.Library()


# 返回所以分类
@register.simple_tag()
def categories():
    return Category.objects.all()


# 根据Email生成头像地址
@register.filter(name='gravatar')
def gravatar(email, size=32):
    return "https://gravatar.com/avatar/%s?s=%s&d=identicon" % (
        hashlib.md5(email.lower().encode()).hexdigest(), str(size))
