import mistune
from django import template


register = template.Library()


class CustomRender(mistune.Renderer):
    pass


@register.filter(name='markdown')
def markdown(value):
    return mistune.Markdown(renderer=CustomRender())(value)
