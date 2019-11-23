from django.forms import widgets
from django.utils.safestring import mark_safe


class TextInputMarkdown(widgets.Textarea):
    """
    please see: https://github.com/pandao/editor.md
    """
    def render(self, name, value, attrs=None, renderer=None):
        html = '''
        <div id="editor">
            <textarea name="%(name)s" style="display:none;">%(body)s</textarea>
        </div>
        <script type="text/javascript">
            $(function(){
                var editor = editormd("editor",{
                    height: 600,
                    path: "%(path)s"
                });
            });
        </script>
    ''' % {
            'name': name,
            'body': value,
            'path': '//cdn.jsdelivr.net/gh/pandao/editor.md@1.5.0/lib/',
        }
        return mark_safe(html)

    class Media:
        css = {
            "all": ("//cdn.jsdelivr.net/gh/pandao/editor.md@1.5.0/css/editormd.min.css",)
        }
        js = (
            "//cdn.jsdelivr.net/gh/pandao/editor.md@1.5.0/editormd.min.js",
            "//cdn.jsdelivr.net/npm/jquery@3.3.1/dist/jquery.min.js"
        )
