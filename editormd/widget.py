from django.forms import widgets
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class TextInputMarkdown(widgets.Textarea):
    """
    please see:
        https://github.com/pandao/editor.md
        https://github.com/pylixm/django-mdeditor
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lib_path = '//cdn.jsdelivr.net/gh/pandao/editor.md@1.5.0/lib/'

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''

        return mark_safe(render_to_string("editormd.html", {
            "body": value,
            "path": self.lib_path,
        }))

    class Media:
        css = {
            "all": ("//cdn.jsdelivr.net/gh/pandao/editor.md@1.5.0/css/editormd.min.css",)
        }
        js = (
            "//cdn.jsdelivr.net/npm/jquery@3.3.1/dist/jquery.min.js",
            "//cdn.jsdelivr.net/gh/pandao/editor.md@1.5.0/editormd.min.js",
        )
