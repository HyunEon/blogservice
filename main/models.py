from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.core.files.base import ContentFile
from .tasks import generate_thumbnail_async
from mptt.models import MPTTModel, TreeForeignKey
from bs4 import BeautifulSoup
from PIL import Image
from unidecode import unidecode
from io import BytesIO
import uuid, requests

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
    blog_description = models.CharField(max_length=100, blank=True, null=True, help_text='블로그 소개', default='새로운 블로그입니다.')
    # User > settings.AUTH_USER_MODEL로 변경
    blog_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bloginfo")
    blog_created_date = models.DateTimeField(auto_now_add=True, help_text='블로그 만들어진 날짜')
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text='사용자 ID를 슬러그로 받음')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.blog_title

# django mptt 모델로 재구성
# depth + CRUD + 순서 변경이 들어가는 카테고리 트리를 인덱스 값 하나로 일일이 업데이트 하는 구조는 구현 난이도도 매우매우 어렵고..
# 인덱스 하나 업데이트 할 때마다 쿼리가 들어가니 성능적으로도 매우 비효율적이었다.
# nestable + mptt 모델을 활용
class BlogCategory(MPTTModel):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    category_name = models.CharField(max_length=50)
    category_for = models.ForeignKey(BlogInfo, on_delete=models.CASCADE, related_name='categories')
    category_order = models.PositiveIntegerField(default=0)
    category_isopen = models.BooleanField(default=False, help_text="카테고리 펼침 여부 결정")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    slug = models.SlugField(max_length=100, blank=True, help_text='카테고리 이름을 슬러그로 받음')

    # 기본 정렬 기준 값
    class MPTTMeta:
        order_insertion_by = ['category_order']

    class Meta:
        ordering = ['category_order']
        unique_together = ('category_for', 'slug')

    def save(self, *args, **kwargs):
        # 이름이 변경될 때마다 slug를 자동 업데이트
        base_slug = slugify(unidecode(self.category_name), allow_unicode=True)
        final_slug = base_slug
        num = 1

        # 기존 slug와 겹치면 숫자 붙이기
        while BlogCategory.objects.filter(slug=final_slug).exclude(pk=self.pk).exists():
            final_slug = f"{base_slug}-{num}"
            num += 1

        self.slug = final_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name
    
class PostContents(models.Model):
    post_id = models.AutoField(primary_key=True, help_text='블로그 포스트 id')
    post_title = models.CharField(max_length=20, null = False, db_index= True, help_text='블로그 포스트 제목 필드')
    post_contents = CKEditor5Field('Text', config_name='extends')
    post_date = models.DateTimeField(auto_now_add=True, help_text='블로그 포스트 날짜')
    post_editdate = models.DateTimeField(null=True, blank=True, help_text='블로그 포스트 수정된 날짜, 해당 필드에 값 유무로 포스트 수정 여부를 판단함')
    # BlogInfo 외래 키로 연결, 이 스키마로 블로그 작성자, 정보 모두 접근할 수 있으므로 포스트 작성자 스키마는 삭제함.
    post_blog = models.ForeignKey(BlogInfo, on_delete=models.CASCADE, null=True, related_name='posts', help_text='포스트가 속한 블로그')
    # BlogCategory와 외래 키로 연결, 카테고리가 삭제되면 포스트도 삭제되도록 동작 변경
    post_category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='categories', help_text='포스트가 속한 카테고리')
    # 0 이하의 값은 저장할 필요가 없으므로 PositiveIntegerField 지정
    post_view_count = models.PositiveIntegerField(default=0, help_text='조회수 값')
    post_thumbnail = models.ImageField(upload_to="posts/thumbnails/", null=True, blank=True, help_text='포스트 썸네일')
    slug = models.SlugField(max_length=100, blank=True, help_text='포스트 제목을 슬러그로 받음')
    # 포스트 제목 정렬 값
    title_align = models.CharField(max_length=10, choices=[('left','왼쪽'), ('center','가운데'), ('right','오른쪽')], default='left', help_text='포스트 제목 정렬')
    
    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.post_title

    def save(self, *args, **kwargs):
        # 새로 생성 중인지 확인
        creating = self._state.adding
        super().save(*args, **kwargs)

        # 새로 생성 and 썸네일이 없으면 생성
        # 썸네일 생성 작업은 Celery로 비동기 처리
        if creating and not self.post_thumbnail:
            generate_thumbnail_async.delay(self.post_id)

    # @property를 붙이면 파이썬은 해당 함수를 getter로 인식함. 
    # 따라서 Django ORM의 역참조로, related_name으로 지정한 likes와 comments를 가져와 count()해서 리턴함.
    @property
    def like_count(self):
        return self.likes.count()

    def comments_count(self):
        return self.comments.count()
        
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

class PostLike(models.Model):
    like_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    like_post = models.ForeignKey(PostContents, on_delete=models.CASCADE, related_name='likes')
    like_created_at = models.DateTimeField(auto_now_add=True)

     # 한 사용자는 한 포스트에 중복으로 좋아요를 할 수 없게, unique_together로 묶음.
    class Meta:
        unique_together = ('like_user', 'like_post')

    def __str__(self):
        return f"{self.like_user} → {self.like_post}"

class Notification(models.Model):
    # 오.. 이렇게 미리 choice를 정의해둘 수도 있다..
    NOTIF_TYPE = [
        ('comment', 'Comment'),
        ('reply', 'Reply'),
        ('like', 'Like'),
    ]
    # 기본 유저 모델을 이렇게 settings.py에서 끌어올 수도 있었다..!
    notification_receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIF_TYPE, help_text='알림 타입: 좋아요, 댓글 등등')
    notification_message = models.TextField(help_text='알림 내용')
    notification_url = models.CharField(max_length=255, blank=True, help_text='알림 바로가기 url')
    notification_is_read = models.BooleanField(default=False, help_text='알림 읽었는지 여부')
    notification_created_at = models.DateTimeField(default=timezone.now, help_text='만들어진 시간')

    # 기본 정렬을 이렇게 정의할 수 있었다.. 우선 최신순 정렬
    class Meta:
        ordering = ['-notification_created_at']
    
# Access model field values using Python attributes.
#print(record.id) # should return 1 for the first record.
#print(record.my_field_name) # should print 'Instance #1'

# Change record by modifying the fields, then calling save().
#record.my_field_name = "New Instance Name"

# Create a new record using the model's constructor.
#record = MyModelName(my_field_name="Instance #1")

# Save the object into the database.
#record.save()
