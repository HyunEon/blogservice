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
from django.views.generic import RedirectView
from django.contrib import admin
from django.urls import path, include
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    path('admin/', admin.site.urls),
    path('auth/google/callback/', views.googlelogin, name='googlelogin'), # GIS url
    path('register/', views.showregister, name='showregister'), # 회원가입 페이지
    path('', views.showmain, name='showmain'), # 메인 페이지
    path('login/', views.loginview, name='login'), # 로그인 페이지에 직접 들어온 경우도 로그인 여부에 따라 리다이렉트
    path('logout/', views.logoutview, name='logout'), # 로그아웃
    path('new/', views.createpost, name='createpost'), # 새로운 포스트 생성
    path('settings/', views.settingspage, name='settingspage'), # 세팅 페이지
    path('category/reorder/', views.reordercategory, name='reordercategory'), # 카테고리 정렬
    path('category/create/', views.createcategory, name='createcategory'), # 카테고리 생성 
    path('category/<uuid:category_id>/update/', views.updatecategory, name='updatecategory'), # 카테고리 이름 수정
    path('category/<uuid:category_id>/delete/', views.deletecategory, name='deletecategory'), # 카테고리 삭제
    path('ckeditor5/', include('django_ckeditor_5.urls')), # ckeditor5가 로딩될 때 필요함.
    path('post/<int:post_id>/like/', views.togglelike, name='togglelike'), # 좋아요 처리
    path('notifications/notificationread/', views.notificationread, name='notificationread'), # 알림 읽음 처리
    path('<slug:blog_slug>/', views.showblog, name='showblog'), # 블로그 페이지
    path('<slug:blog_slug>/category/<slug:category_slug>/', views.showblog, name='showblogbycategory'), # 카테고리 별로 포스트 보기(붙여쓰고 싶었으나 showpostdetail 파라미터 개수와 충돌하여 중간 path 추가..)
    path('<slug:blog_slug>/post/<slug:post_slug>/', views.showpostdetail, name='showpostdetail'), # 포스트 자세히 보기
    path('<slug:blog_slug>/post/<slug:post_slug>/edit/', views.editpost, name='editpost'), # 포스트 업데이트
    path('<slug:blog_slug>/post/<slug:post_slug>/delete/', views.deletepost, name='deletepost'), # 포스트 삭제
    path('<slug:blog_slug>/post/<slug:post_slug>/comments/', views.createcomment, name='createcomment'), # 댓글 생성
    path('<slug:blog_slug>/post/<slug:post_slug>/comments/edit', views.createcomment, name='editcomment'), # 댓글 업데이트, 생성과 로직을 공유함
    path('<slug:blog_slug>/post/<slug:post_slug>/comments/delete', views.deletecomment, name='deletecomment'), # 댓글 삭제
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)