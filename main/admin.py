from django.contrib import admin
from django.contrib.auth import get_user_model 
from .models import PostContents, PostComments, BlogCategory, BlogInfo
User = get_user_model()

# Register your models here.
admin.site.register(PostContents)
admin.site.register(PostComments)
admin.site.register(BlogCategory)
admin.site.register(BlogInfo)
admin.site.register(User)