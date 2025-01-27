from django import forms
from .models import PostContents, PostComments

# 글 쓰기 폼
class CreatePostForm(forms.ModelForm):
    post_id = forms.CharField(widget=forms.HiddenInput())
    post_editor_uid = forms.CharField(widget=forms.HiddenInput())
    # Form에 포함되어야 하지만 프론트에 굳이 나타날 필요가 없는 필드는 HiddenInput 처리해줌

    class Meta:
        model = PostContents
        fields = ['post_id', 'post_title', 'post_contents', 'post_editor_uid', 'post_editdate']
        # exclude = ['post_editdate'] 이 방법으로 post_editdate를 제외한 모든 필드를 정의할 수 있음

class CreateCommentForm(forms.ModelForm):
    comment_id = forms.CharField(widget=forms.HiddenInput())
    comment_order = forms.IntegerField(widget=forms.HiddenInput())
    comment_postadress = forms.CharField(widget=forms.HiddenInput())
    comment_editor_uid = forms.CharField(widget=forms.HiddenInput())
    comment_isreply = forms.BooleanField(widget=forms.HiddenInput())
    comment_replyto = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = PostComments
        fields = ['comment_id', 'comment_order', 'comment_postadress', 'comment_editor_uid', 'comment_contents', 'comment_isreply', 'comment_replyto']