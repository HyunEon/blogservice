"""
URL configuration for blog_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.showmain, name='showmain'), # 메인 페이지
    path('login/', views.loginview, name='loginview'), # 로그인 페이지에 직접 들어온 경우도 로그인 여부에 따라 리다이렉트
    # path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'), 
    path('logout/', views.logoutview, name='logout'), # 로그아웃
    path('post/', views.showpost, name='post_list'),
    path('post/view/<str:category_id>', views.showpostbycategory, name='postbycategory'),
    path('post/new/', views.create_post, name='create_post'),
    path('post/<str:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<str:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<str:post_id>/', views.showpostdetail, name='showpostdetail'),
    path('post/<str:post_id>/comments/', views.createcomment, name='createcomment'),
    path('post/<str:post_id>/comments/<str:comment_id>/', views.createreplycomment, name='createreplycomment'),
    path('post/<str:post_id>/comments/<str:comment_id>/delete', views.deletecomment, name='deletecomment'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)