from django import forms
from .models import PostContents

# 글 쓰기 폼
class CreatePostForm(forms.ModelForm):
    post_id = forms.CharField(widget=forms.HiddenInput())
    post_editor_uid = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = PostContents
        fields = ['post_id', 'post_title', 'post_contents', 'post_editor_uid']
        # exclude = ['post_editdate'] 이 방법으로 post_editdate를 제외한 모든 필드를 정의할 수 있음