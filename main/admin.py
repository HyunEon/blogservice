from django.contrib import admin
from .models import PostContents, PostComments, BlogCategory, BlogInfo


# Register your models here.
admin.site.register(PostContents)
admin.site.register(PostComments)
admin.site.register(BlogCategory)
admin.site.register(BlogInfo)