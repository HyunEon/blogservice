from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
import uuid

# 모델이 생성/변경되면 python manage.py makemigrations로 마이그레이션을 생성한 다음, python manage.py migrate로 적용해줘야 함.
# 관리자 페이지에서 모델을 관리하고 싶다면 admin.py에 모델 정보를 추가해줘야 함.
# sqlite 접속 시 sqlite3 db.sqlite3, 종료 시 .exit 입력.

# Create your models here.

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=20)
    # url 필드랑 엄청나게 고민했는데 어차피 미디어 서버를 별도로 분리시킬 예정이라, 이미지 필드가 관리에 훨씬 용이할 것 같아 다시 롤백
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, default='profile_images/profile_created_by_Gemini.webp')

    def __str__(self):
        return self.username

class BlogInfo(models.Model):
    blog_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, help_text='BlogInfo : CustomUser -> (1:1)')
    # models.CharField(max_length=100, primary_key=True, help_text='blog/_')
    blog_title = models.CharField(max_length=20, db_index= True, help_text='블로그 제목', default='새로운 블로그')
    # User > settings.AUTH_USER_MODEL로 변경
    blog_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bloginfo")
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text='사용자 ID를 슬러그로 받음')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.blog_title

class BlogCategory(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, help_text='BlogInfo : BlogCategory -> (1:N)')
    category_index = models.IntegerField(help_text='카테고리 정렬을 위해 사용되는 인덱스')
    category_name = models.CharField(max_length=20, default='내 글', db_index= True, help_text='카테고리 이름')
    category_for = models.ForeignKey(BlogInfo, on_delete=models.CASCADE, related_name='categories', help_text='카테고리가 적용될 블로그 id')
    category_isdepth = models.BooleanField(help_text='뎁스가 적용된 카테고리 여부 확인')
    category_depth_for = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories', help_text='null시 부모')
    slug = models.SlugField(max_length=100, blank=True, help_text='카테고리 이름을 슬러그로 받음')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.category_name
    
class PostContents(models.Model):
    post_id = models.AutoField(primary_key=True, help_text='블로그 포스트 id')
    post_title = models.CharField(max_length=20, null = False, db_index= True, help_text='블로그 포스트 제목 필드')
    post_contents = CKEditor5Field('Text', config_name='extends')
    post_date = models.DateTimeField(auto_now_add=True, help_text='블로그 포스트 날짜')
    post_editdate = models.DateTimeField(null=True, blank=True, help_text='블로그 포스트 수정된 날짜, 해당 필드에 값 유무로 포스트 수정 여부를 판단함')
    # BlogInfo 외래 키로 연결, 이 스키마로 블로그 작성자, 정보 모두 접근할 수 있으므로 포스트 작성자 스키마는 삭제함.
    post_blog = models.ForeignKey(BlogInfo, on_delete=models.CASCADE, null=True, related_name='posts', help_text='포스트가 속한 블로그')
    # BlogCategory와 외래 키로 연결
    post_category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='categories', help_text='포스트가 속한 카테고리')
    slug = models.SlugField(max_length=100, blank=True, help_text='포스트 제목을 슬러그로 받음')
    # 포스트 제목 정렬 값
    title_align = models.CharField( max_length=10, choices=[('left','왼쪽'), ('center','가운데'), ('right','오른쪽')], default='left', help_text='포스트 제목 정렬')
    
    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.post_title
        
class PostComments(models.Model):
    comment_id = models.AutoField(primary_key=True, help_text='댓글 id')
    comment_order = models.IntegerField(null=False, default=1, help_text='댓글/답글을 정렬하기 위한 순서이자 묶어주기 위한 그룹, 답글의 경우 같은 order로 묶고 생성 날짜로 정렬한다')
    comment_contents = models.TextField(null = False, help_text='댓글 내용')
    comment_date = models.DateTimeField(auto_now_add=True, help_text='댓글 작성한 날짜')
    comment_isreply = models.BooleanField(help_text='답글 여부 확인')
    comment_isdelete = models.BooleanField(help_text='삭제 여부 확인', default=False)
    # PostContents와 외래 키로 연결
    comment_post = models.ForeignKey(PostContents, on_delete=models.CASCADE, null=True, related_name='comments', help_text='댓글이 달린 포스트')
    # BlogInfo 또는 User 모델과 외래 키로 연결 (작성자 정보)
    comment_editor = models.ForeignKey(BlogInfo, on_delete=models.SET_NULL, null=True, related_name='comments', help_text='댓글 작성자')
    mention = models.ForeignKey(CustomUser, null=True, blank=True, related_name='mentioned_comments', on_delete=models.SET_NULL, help_text='@멘션')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.comment_editor
    
# Access model field values using Python attributes.
#print(record.id) # should return 1 for the first record.
#print(record.my_field_name) # should print 'Instance #1'

# Change record by modifying the fields, then calling save().
#record.my_field_name = "New Instance Name"

# Create a new record using the model's constructor.
#record = MyModelName(my_field_name="Instance #1")

# Save the object into the database.
#record.save()
