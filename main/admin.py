from django.contrib import admin
from django.contrib.auth import get_user_model 
from mptt.admin import DraggableMPTTAdmin
from .models import PostContents, PostComments, BlogCategory, BlogInfo
User = get_user_model()

@admin.register(BlogInfo)
class BlogInfoAdmin(admin.ModelAdmin):
    list_display = ('blog_title', 'blog_user', 'blog_created_date', 'slug')
    search_fields = ('blog_title', 'blog_user__username')
    list_filter = ('blog_created_date',)

class CategoryAdmin(DraggableMPTTAdmin):
    list_display = (
        'tree_actions',
        'indented_title',
        'category_name',
        'slug',
    )
    prepopulated_fields = {'slug': ('category_name',)}
    mptt_level_indent = 20


# Register your models here.
admin.site.register(PostContents)
admin.site.register(PostComments)
admin.site.register(BlogCategory, CategoryAdmin)
admin.site.register(User)