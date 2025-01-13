from django.contrib import admin
from .models import PostContents, PostComments, MediaContent


# Register your models here.
admin.site.register(PostContents)
admin.site.register(PostComments)
admin.site.register(MediaContent)