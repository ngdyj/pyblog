from django import template
from ..models import Category

register = template.Library()

# 返回所以分类
@register.simple_tag()
def categories():
    return Category.objects.all()
