from django import forms
from .models import PostContents, PostComments

# 글 쓰기 폼
class PostForm(forms.ModelForm):
    class Meta:
        model = PostContents
        fields = ['post_id', 'post_category_for', 'post_title', 'post_contents', 'post_editor_uid']
        # exclude = ['post_editdate'] 이 방법으로 post_editdate를 제외한 모든 필드를 정의할 수 있음

class CommentForm(forms.ModelForm):
    class Meta:
        model = PostComments
        fields = ['comment_id', 'comment_order', 'comment_postadress', 'comment_editor_uid', 'comment_contents', 'comment_isreply', 'comment_replyto']