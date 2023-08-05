from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Comment, Post


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pub_date'].initial = timezone.localtime(
            timezone.now()).strftime('%Y-%m-%dT%H:%M')

    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'image', 'location', 'category']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
