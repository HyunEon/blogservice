from django.db import models

# 모델이 생성/변경되면 python manage.py makemigrations로 마이그레이션을 생성한 다음, python manage.py migrate로 적용해줘야 함.
# 관리자 페이지에서 모델을 관리하고 싶다면 admin.py에 모델 정보를 추가해줘야 함.

# Create your models here.
class PostContents(models.Model):
    post_index = models.IntegerField(primary_key=True, null=False, auto_created=True, help_text='블로그 포스트 인덱스')
    post_id = models.CharField(max_length=100, help_text='블로그 포스트 id 아마 GUID로 설정될 듯')
    post_title = models.CharField(max_length=20, db_index= True, help_text='블로그 포스트 제목 필드')
    post_contents =  models.TextField(null = False, help_text='블로그 포스트 내용 필드')
    post_date = models.DateTimeField(auto_now_add=True, help_text='블로그 포스트 날짜')
    post_editdate = models.DateTimeField(auto_now=True, help_text='블로그 포스트 수정된 날짜') # 필요 있을진 모르겠음
    post_editor_uid = models.CharField(max_length=20, help_text='포스트 작성자 uid')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.post_title
    
class PostComments(models.Model):
    comment_index = models.IntegerField(primary_key=True, auto_created=True, help_text='댓글 인덱스')
    comment_id = models.CharField(max_length=100, help_text='댓글 id 형식은 GUID + 숫자 4자리')
    comment_postadress = models.CharField(max_length=50, help_text='댓글이 달린 포스트 주소')
    comment_editor_uid = models.CharField(max_length=20, help_text='댓글 작성자 uid')
    comment_contents = models.TextField(null = False, help_text='댓글 내용')
    comment_date = models.DateTimeField(auto_now_add=True, help_text='댓글 작성한 날짜')
    comment_isreply = models.BooleanField(help_text='답글 여부 확인')
    comment_replyto = models.CharField(max_length=100, null=True, blank= True, help_text='답글 주소 id, 댓글 ID를 여기다 넣음')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.comment_postadress
    
# 미디어(사진, 동영상, 파일 포함)가 업로드되는 테이블.. 을 따로 만들었으나 CKeditor를 사용해보니 플러그인 단에서 경로만 지정해주면 자체적으로 지원되는 것 같다.
class MediaContent(models.Model):
    media_index = models.IntegerField(primary_key=True, auto_created=True, help_text='미디어 인덱스')
    media_id = models.CharField(max_length=100, help_text='미디어 id')
    media_name = models.CharField(max_length=100, help_text='미디어 파일 이름름')
    media_date = models.DateTimeField(auto_now=True, help_text='미디어가 업로드된 날짜')
    media_contents = models.TextField(help_text='미디어 데이터, base64로 인코딩해서 넣을듯, 사진이면 Webp를 적용하고 싶음')

    def __str__(self):
        return self.media_name

# Access model field values using Python attributes.
#print(record.id) # should return 1 for the first record.
#print(record.my_field_name) # should print 'Instance #1'

# Change record by modifying the fields, then calling save().
#record.my_field_name = "New Instance Name"

# Create a new record using the model's constructor.
#record = MyModelName(my_field_name="Instance #1")

# Save the object into the database.
#record.save()
