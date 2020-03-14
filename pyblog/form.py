from django.forms import ModelForm
from django import forms
from .models import Article
from editormd.widget import TextInputMarkdown


class ArticleAdminForm(ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'content': TextInputMarkdown(),
        }


class CommentForm(forms.Form):
    email = forms.EmailField(label='email', max_length=100,)
    nick = forms.CharField(label='nick', max_length=20)
    parent_id = forms.IntegerField(label='parent_id', required=False)
    at_id = forms.IntegerField(label='at_id', required=False)
    content = forms.CharField(label='content', max_length=50)


class InfoAdminForm(ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'content': TextInputMarkdown(),
        }
