from django.db import models

# 모델이 생성/변경되면 python manage.py makemigrations로 마이그레이션을 생성한 다음, python manage.py migrate로 적용해줘야 함.
# 관리자 페이지에서 모델을 관리하고 싶다면 admin.py에 모델 정보를 추가해줘야 함.

# Create your models here.
class MyModel(models.Model):
    post_title = models.CharField(max_length=20, db_index= True, help_text='블로그 포스트 제목 필드')
    post_contents = models.TextField(null = True, help_text='블로그 포스트 내용 필드')

    def __str__(self):
        """String for representing the MyModel object (in Admin site etc.)."""
        return self.post_title

# Access model field values using Python attributes.
#print(record.id) # should return 1 for the first record.
#print(record.my_field_name) # should print 'Instance #1'

# Change record by modifying the fields, then calling save().
#record.my_field_name = "New Instance Name"

# Create a new record using the model's constructor.
#record = MyModelName(my_field_name="Instance #1")

# Save the object into the database.
#record.save()
