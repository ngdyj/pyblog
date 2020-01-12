from django import template
from ..models import Category, Tag
from ..settings import AVATAR_DOMAIN
from datetime import datetime
import hashlib
import re
import math

register = template.Library()


# 返回所以分类
@register.simple_tag()
def categories():
    return Category.objects.all()


@register.simple_tag()
def tags():
    return Tag.objects.all()


# 根据Email生成头像地址
@register.filter(name='gravatar')
def gravatar(email, size=32):
    return "%s/avatar/%s?s=%s&d=retro" % (AVATAR_DOMAIN,
                                          hashlib.md5(email.lower().encode()).hexdigest(), str(size))


@register.filter(name='mod')
def mod(num, val):
    # 取模运算
    if str(num).isdigit() and str(val).isdigit():
        if val == 0:
            return 0
        return num % val
    return 0


# 预计阅读用时
@register.filter(name='get_read_time')
def get_read_time(content) -> int:
    words = re.findall(r"\w+", content)
    return math.ceil(len(words) / 300)


# 时间显示方式
@register.filter(name='human_date')
def human_date(d: datetime) -> str:
    now = datetime.now()
    if d.year == now.year:
        if d.month == now.month and d.day == now.day:
            return "{0} hours ago".format(d.hour)
        elif d.month == now.month:
            return "{0} days ago".format(now.day - d.year)
        else:
            return "{0} month ago".format(now.month - d.month)
    elif now.year - d.year >= 2:
        return "{0} year ago".format(now.year - d.year)
    else:
        return "{0} month ago".format(now.month + 12 - d.month)


