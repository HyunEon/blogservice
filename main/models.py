from django.db import models

# 모델이 생성/변경되면 python manage.py makemigrations로 마이그레이션을 생성한 다음, python manage.py migrate로 적용해줘야 함.
# 관리자 페이지에서 모델을 관리하고 싶다면 admin.py에 모델 정보를 추가해줘야 함.

# Create your models here.
class BlogInfo(models.Model):
    blog_id = models.CharField(max_length=100, help_text='블로그 id https://ex.com/blog/-------/')
    blog_title = models.CharField(max_length=20, db_index= True, help_text='블로그 제목')
    blog_user = models.CharField(max_length=20, help_text='블로그 uid')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.blog_title
class BlogCategory(models.Model):
    category_index = models.IntegerField(primary_key=True, auto_created=True, help_text='카테고리 인덱스')
    category_id = models.CharField(max_length=100, help_text='카테고리 id')
    category_name = models.CharField(max_length=20, default='내 글', db_index= True, help_text='카테고리 제목')
    category_for = models.CharField(max_length=100, help_text='카테고리가 적용될 블로그 주소')
    category_isdepth = models.BooleanField(help_text='뎁스가 적용된 카테고리 여부 확인')
    category_depth_for = models.CharField(max_length=100, null=True, blank=True, help_text='뎁스가 적용된 카테고리의 부모 카테고리 id')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.category_id
    
class PostContents(models.Model):
    post_index = models.IntegerField(primary_key=True, null=False, auto_created=True, help_text='블로그 포스트 인덱스')
    post_category_for = models.CharField(max_length=100, help_text='카테고리 id')
    post_id = models.CharField(max_length=100, help_text='블로그 포스트 id 아마 GUID로 설정될 듯')
    post_title = models.CharField(max_length=20, null = False, db_index= True, help_text='블로그 포스트 제목 필드')
    post_contents =  models.TextField(null = False, help_text='블로그 포스트 내용 필드')
    post_date = models.DateTimeField(auto_now_add=True, help_text='블로그 포스트 날짜')
    post_editdate = models.DateTimeField(null= True, help_text='블로그 포스트 수정된 날짜')
    post_editor_uid = models.CharField(max_length=20, help_text='포스트 작성자 uid')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.post_title
    
class PostComments(models.Model):
    comment_index = models.IntegerField(primary_key=True, auto_created=True, help_text='댓글 인덱스')
    comment_order = models.IntegerField(null=False, default=1, help_text='댓글/대댓글을 정렬하기 위한 순서이자 묶어주기 위한 그룹 대댓글의 경우 같은 order로 묶고 생성 날짜로 정렬한다')
    comment_id = models.CharField(max_length=100, help_text='댓글 id 형식은 GUID')
    comment_postadress = models.CharField(max_length=50, help_text='댓글이 달린 포스트 주소')
    comment_editor_uid = models.CharField(max_length=20, help_text='댓글 작성자 uid')
    comment_contents = models.TextField(null = False, help_text='댓글 내용')
    comment_date = models.DateTimeField(auto_now_add=True, help_text='댓글 작성한 날짜')
    comment_isreply = models.BooleanField(help_text='답글 여부 확인')
    comment_isdelete = models.BooleanField(help_text='삭제 여부 확인', default=False)
    comment_replyto = models.CharField(max_length=100, null=True, blank= True, help_text='답글 주소 id, 댓글 ID를 여기다 넣음, 근데 order 스키마로 충분한 것 같아 제거해야 하나 고민중')

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
