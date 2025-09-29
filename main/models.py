from django.db import models
from django.contrib.auth.models import User

# 모델이 생성/변경되면 python manage.py makemigrations로 마이그레이션을 생성한 다음, python manage.py migrate로 적용해줘야 함.
# 관리자 페이지에서 모델을 관리하고 싶다면 admin.py에 모델 정보를 추가해줘야 함.

# Create your models here.
class BlogInfo(models.Model):
    blog_id = models.CharField(max_length=100, primary_key=True, help_text='블로그 id https://ex.com/blog/-------/')
    blog_title = models.CharField(max_length=20, db_index= True, help_text='블로그 제목')
    blog_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="bloginfo")

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.blog_title
class BlogCategory(models.Model):
    category_id = models.CharField(max_length=100, help_text='카테고리 id')
    category_index = models.IntegerField(primary_key=True, auto_created=True, help_text='카테고리 인덱스')
    category_name = models.CharField(max_length=20, default='내 글', db_index= True, help_text='카테고리 제목')
    # BlogInfo 외래 키로 연결
    category_for = models.ForeignKey(BlogInfo, on_delete=models.CASCADE, related_name='categories', help_text='카테고리가 적용될 블로그 id')
    category_isdepth = models.BooleanField(help_text='뎁스가 적용된 카테고리 여부 확인')
    category_depth_for = models.CharField(max_length=100, null=True, blank=True, help_text='뎁스가 적용된 카테고리의 부모 카테고리 id')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.category_id
    
class PostContents(models.Model):
    post_id = models.IntegerField(primary_key=True, null=False, auto_created=True, help_text='블로그 포스트 id')
    post_title = models.CharField(max_length=20, null = False, db_index= True, help_text='블로그 포스트 제목 필드')
    post_contents =  models.TextField(null = False, help_text='블로그 포스트 내용 필드')
    post_date = models.DateTimeField(auto_now_add=True, help_text='블로그 포스트 날짜')
    post_editdate = models.DateTimeField(null=True, blank=True, help_text='블로그 포스트 수정된 날짜, 해당 필드에 값 유무로 포스트 수정 여부를 판단함')
    # BlogInfo 또는 User 모델과 외래 키로 연결 (작성자 정보)
    # post_editor = models.ForeignKey(BlogInfo, on_delete=models.SET_NULL, null=True, related_name='comments', help_text='댓글 작성자')
    # BlogInfo 외래 키로 연결
    post_blog = models.ForeignKey(BlogInfo, on_delete=models.CASCADE, null=True, related_name='posts', help_text='포스트가 속한 블로그')
    # BlogCategory와 외래 키로 연결
    post_category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts', help_text='포스트가 속한 카테고리')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.post_title
    
class PostComments(models.Model):
    comment_id = models.CharField(max_length=100, help_text='댓글 id')
    comment_index = models.IntegerField(primary_key=True, auto_created=True, help_text='댓글 인덱스')
    comment_order = models.IntegerField(null=False, default=1, help_text='댓글/대댓글을 정렬하기 위한 순서이자 묶어주기 위한 그룹 대댓글의 경우 같은 order로 묶고 생성 날짜로 정렬한다')
    comment_contents = models.TextField(null = False, help_text='댓글 내용')
    comment_date = models.DateTimeField(auto_now_add=True, help_text='댓글 작성한 날짜')
    comment_isreply = models.BooleanField(help_text='답글 여부 확인')
    comment_isdelete = models.BooleanField(help_text='삭제 여부 확인', default=False)
    # PostContents와 외래 키로 연결
    comment_post = models.ForeignKey(PostContents, on_delete=models.CASCADE, null=True, related_name='comments', help_text='댓글이 달린 포스트')
    # BlogInfo 또는 User 모델과 외래 키로 연결 (작성자 정보)
    comment_editor = models.ForeignKey(BlogInfo, on_delete=models.SET_NULL, null=True, related_name='comments', help_text='댓글 작성자')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.comment_postadress
    
# Access model field values using Python attributes.
#print(record.id) # should return 1 for the first record.
#print(record.my_field_name) # should print 'Instance #1'

# Change record by modifying the fields, then calling save().
#record.my_field_name = "New Instance Name"

# Create a new record using the model's constructor.
#record = MyModelName(my_field_name="Instance #1")

# Save the object into the database.
#record.save()
