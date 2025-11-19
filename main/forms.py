from django import forms
from .models import PostContents, BlogCategory, PostComments, BlogInfo
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db.models import Max
from mptt.forms import TreeNodeChoiceField

User = get_user_model()

# 회원가입 폼
class RegisterForm(UserCreationForm):
    email_id = forms.CharField(label="이메일 아이디", max_length=64)
    email_domain = forms.CharField(label="도메인", max_length=64)
    nickname = forms.CharField(label="닉네임", max_length=20, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 비밀번호 필드 위젯에 속성 추가 ('password1')
        # https://docs.djangoproject.com/en/5.2/ref/forms/widgets/
        self.fields['password1'].widget.attrs.update({
            'oncopy': 'return false',
            'oncut': 'return false',
            'onpaste': 'return false',
            'autocomplete': 'off', # 자동 완성 방지
        })
        
        # 비밀번호 확인 필드 ('password2')
        self.fields['password2'].widget.attrs.update({
            'oncopy': 'return false',
            'oncut': 'return false',
            'onpaste': 'return false',
            'autocomplete': 'off',
        })
        
    class Meta(UserCreationForm.Meta):
        # CustomUser 모델 사용
        model = User
        # 폼의 Meta 클래스에 지정된 필드 목록을 확장, User 모델에 email 필드가 있으므로 해당 스키마를 사용함.
        fields = UserCreationForm.Meta.fields + ('email', 'nickname')
        pass

    def clean(self):
        # views.py에서 form_is_vaild() 유효성 검사 호출 시 훅(Hook)되면서 해당 메서드 호출
        # clean()은 form 안에서 validate된 데이터만 걸러내서 cleaned_data에 따로 취합하여 반환함.
        cleaned_data = super().clean()
        email_id = cleaned_data.get('email_id')
        email_domain = cleaned_data.get('email_domain')

        if email_id and email_domain:
            # 이메일 주소 합치기
            email = f"{email_id}@{email_domain}"
            cleaned_data['email'] = email
        else:
            raise forms.ValidationError("이메일 주소와 도메인을 모두 입력해주세요.")
        return cleaned_data

    def save(self, commit=True):
        # # form.save() 호출 시 이 메서드가 실행된다. cleaned_data된 email 데이터를 여기서 추가로 넣어준다.
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nickname = self.cleaned_data.get('nickname')
        if commit:
            user.save()
        return user

# 사용자 업데이트 폼
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image', 'nickname']  # 수정 가능 항목

    def save(self, commit=True):
        # # form.save() 호출 시 이 메서드가 실행된다. cleaned_data된 email 데이터를 여기서 추가로 넣어준다.
        user = super().save(commit=False)
        user.nickname = self.cleaned_data.get('nickname')
        if commit:
            user.save()
        return user

# 블로그 업데이트 폼
class BlogUpdateForm(forms.ModelForm):
    class Meta:
        model = BlogInfo
        fields = ['blog_title', 'blog_description']  # 수정 가능 항목

    def save(self, commit=True):
        # # form.save() 호출 시 이 메서드가 실행된다. cleaned_data된 email 데이터를 여기서 추가로 넣어준다.
        blog = super().save(commit=False)
        blog.blog_title = self.cleaned_data.get('blog_title')
        blog.blog_description = self.cleaned_data.get('blog_description')
        if commit:
            blog.save()
        return blog

# 포스트 폼
class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        blog = kwargs.pop('blog', None)
        super().__init__(*args, **kwargs)

        # 블로그 객체로 카테고리 필터링
        if blog:
            self.fields['post_category'].queryset = BlogCategory.objects.filter(category_for=blog)
        else:
            # 없으면 빈 선택지를 보여줌
            self.fields['post_category'].queryset = BlogCategory.objects.none()

        # django에서 생성하는 빈 선택지 제거
        self.fields['post_category'].empty_label = None

    class Meta:
        model = PostContents
        # 사용자가 수정할 수 있는 필드
        fields = ['post_title', 'title_align', 'post_contents', 'post_category'] 
        widgets = {
            'post_title': forms.TextInput(attrs={'class': 'post-title-input'}),
            'post_category': forms.Select(attrs={'class': 'post-category-selector'}),
            'title_align': forms.RadioSelect(attrs={'class': 'title-align-radio'}),
        }

    def clean(self):
        cleaned_data = super().clean() 
        title = cleaned_data.get('post_title')
        post_contents = cleaned_data.get('post_contents')
        category = cleaned_data.get('post_category')
        
        if not title:
            self.add_error('post_title', "제목을 입력해주세요!")
        if not post_contents:
            self.add_error('post_contents', "본문을 입력해주세요!")
        if not category:
            self.add_error('post_category', "카테고리를 선택해주세요!")
        return cleaned_data

# 댓글 폼
class CommentForm(forms.ModelForm):
    parent_comment = None  # 답글일 경우 부모 댓글

    def __init__(self, *args, **kwargs):
        self.post = kwargs.pop('post', None)       # PostContents 객체
        self.editor = kwargs.pop('editor', None)   # BlogInfo 객체
        self.parent_comment = kwargs.pop('parent_comment', None)  # 답글이면 부모
        self.comment_id = kwargs.pop('comment_id', None) # 수정 모드로 들어오면 comment_id가 파라미터로 들어옴
        super().__init__(*args, **kwargs)

        self.fields['mention'].required = False # 멘션은 필수값 해제
        self.fields['mention'].queryset = User.objects.all() # 선택 가능한 유저 지정

    def save(self, commit=True):
        comment = super().save(commit=False)

        # 수정 모드가 아니면 생성
        if self.comment_id is None:
            # 필수 관계 필드 자동 지정
            comment.comment_post = self.post
            comment.comment_editor = self.editor

            # 답글 여부
            comment.comment_isreply = bool(self.parent_comment)

            # comment_order 결정
            if self.parent_comment:
                # 답글이면 부모와 같은 order
                comment.comment_order = self.parent_comment.comment_order
            else:
                # 일반 댓글이면 post 내 최대 order +1
                last_order = PostComments.objects.filter(comment_post=self.post).aggregate(max_order=Max('comment_order'))['max_order'] or 0
                comment.comment_order = last_order + 1
        # 기존 댓글 수정
        else:  
            comment = self.comment_id
            comment.comment_contents = self.cleaned_data['comment_contents']
        if commit:
            comment.save()
        return comment

    class Meta:
        model = PostComments
        fields = ['comment_contents', 'mention']
        widgets = {
            'comment_contents': forms.Textarea(attrs={
                'placeholder': '따뜻한 댓글을 남겨주세요.',
                'class': 'comment-contents-input',
                'rows': 3
            }),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ['category_name', 'category_isopen'] 
        widgets = {
            'category_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category_isopen': forms.CheckboxInput(),
        }
        labels = {
            'category_name': '카테고리 이름',
            'category_isopen': '카테고리 펼침 여부 선택',
        }