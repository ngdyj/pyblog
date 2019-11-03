from django.forms import ModelForm
from .models import Article
from editormd.widget import TextInputMarkdown


class ArticleAdminForm(ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'content': TextInputMarkdown(),
        }
