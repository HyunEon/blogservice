from django import forms
from .models import PostContents, PostComments

# 글 쓰기 폼
class PostForm(forms.ModelForm):
    class Meta:
        model = PostContents
        # 사용자가 직접 입력해야 하는 필드만 포함
        fields = ['post_title', 'post_contents', 'post_category'] 
        # 'post_id', 'post_blog' 필드는 뷰에서 자동으로 설정되므로 제외

class CommentForm(forms.ModelForm):
    class Meta:
        model = PostComments
        # 사용자가 직접 입력해야 하는 필드만 포함
        fields = ['comment_contents']
        # 'comment_id', 'comment_order', 'comment_post', 'comment_editor'는 뷰에서 자동으로 처리

# 글 쓰기 폼
'''class PostForm(forms.ModelForm):
    class Meta:
        model = PostContents
        fields = ['post_id', 'post_category', 'post_title', 'post_contents', 'post_editor']
        # exclude = ['post_editdate'] 이 방법으로 post_editdate를 제외한 모든 필드를 정의할 수 있음

class CommentForm(forms.ModelForm):
    class Meta:
        model = PostComments
        fields = ['comment_id', 'comment_order', 'comment_postadress', 'comment_editor', 'comment_contents', 'comment_isreply']'''