from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.http import Http404, JsonResponse
from django.db import transaction, IntegrityError
from django.db.models import Q, Max, Min
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from .models import BlogInfo, PostContents, PostComments, BlogCategory
from .forms import PostForm, CommentForm, RegisterForm, UserUpdateForm
from unidecode import unidecode
import uuid, os, re, random, json, requests, datetime

from google.oauth2 import id_token
from google.auth.transport import requests as grequests

User = get_user_model()

# Create your views here.
def showregister(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 폼 유효성 검사를 통과했을 때, UserCreationForm 저장 및 블로그 객체 생성(둘 다 반드시 처리되어야 하므로 DB 트랜잭션으로 처리한다.)
            try:
                # DB 트랜잭션으로 처리
                with transaction.atomic():
                    # 사용자 객체 생성
                    instance = form.save()
                    # 블로그 객체 생성 및 슬러그 지정(슬러그: 사용자 ID)
                    blog = BlogInfo.objects.create(blog_user=instance, slug=instance.username)
                    # 블로그 카테고리 기본 생성
                    BlogCategory.objects.create(
                        category_index=1,
                        category_name="내 글",
                        category_for=blog,
                        category_isdepth=False,
                        category_depth_for=None,
                        slug=slugify(unidecode("내 글"))
                    )
                    # django message - https://docs.djangoproject.com/en/5.0/ref/contrib/messages/
                messages.success(request, "✅ 회원가입이 완료되었어요!")
                return redirect(loginview)  # 가입 후 로그인 페이지 등으로 이동
            except Exception as e:
                messages.error(request, f"🚨 이런.. 회원가입 중 오류가 발생했어요!: {e}")
    else:
        form = RegisterForm()
    return render(request, "main/register.html", {"form": form})

# Google 회원가입/로그인, 기존 Django 세션과 연동에 문제가 있어, Custom 세션 사용.
@csrf_exempt
def googlelogin(request):
    # 구글 로그인 버튼에서 받은 next 파라미터 빼기, 없으면 메인
    next_url = request.GET.get('your_own_param_next', '/')
    print(next_url)
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed")

    credential = request.POST.get("credential")
    if not credential:
        return HttpResponseBadRequest("No credential provided", status=400)

    try:
        # 토큰 검증
        idinfo = id_token.verify_oauth2_token(
            credential,
            grequests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

    except ValueError:
        return HttpResponseBadRequest("Invalid token")

    # authenticate 호출 (idinfo를 전달)
    # Django는 settings.AUTHENTICATION_BACKENDS를 순회하며
    # idinfo를 받는 authenticate 메소드를 찾아 실행합니다.
    user = authenticate(request, idinfo=idinfo) 

    if user is not None:
        # authenticate가 성공하면 user 객체에 .backend 속성이 자동으로 붙음
        login(request, user) 
        messages.success(request, f"✅ {user.nickname}님, 환영합니다 😊")
        # 사용자가 보고 있던 페이지가 있으면 해당 페이지로 리디렉트, 없으면 메인으로
        return redirect(next_url)
    else:
        # 인증 실패
        messages.error(request, "⚠️ 로그인에 실패했습니다. 유효하지 않은 사용자입니다.")
        return redirect(loginview)

def loginview(request):
    # 이미 로그인 되어 있으면 main으로 리다이렉트
    if request.user.is_authenticated:
        return redirect(showmain)
    # 로그인 요청 시
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # 폼이 유효하면 사용자를 로그인시키고 메인 페이지로 리다이렉트
            user = form.get_user()
            login(request, user)
            messages.success(request, f"✅ {user.nickname}님, 환영합니다 😊")
            # 사용자가 보고 있던 페이지가 있으면 해당 페이지로 리디렉트, 없으면 메인으로
            next_url = request.GET.get('next') or request.POST.get('next') or '/'
            return redirect(next_url)
    else:
    # GET 요청이면 빈 로그인 폼을 보여줌
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

@login_required
def logoutview(request):
    logout(request)
    messages.info(request, "ℹ️ 로그아웃 했어요! 다음에 또 봐요 👋")
    return redirect(loginview)

def showmain(request):
    # 추천 블로그 3개 가져옴, 추후 첫 블로그와 마지막 블로그 인덱스 값을 가져와 랜덤한 값을 생성하는 로직을 적용
    bloglist = BlogInfo.objects.all()[:3]
    return render(request, 'main/mainpage.html', {'bloglist': bloglist})

@login_required
def updateprofile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ 프로필을 성공적으로 아주 멋지게 수정했어요!')
            return redirect(showmain)  # 수정 후 이동할 페이지
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'main/settings/userprofile.html', {'form': form})

# 하위 카테고리 찾는 로직
def getsubcategories(category):
    # 파라미터로 받은 카테고리의 하위 카테고리를 모두 가져옴
    subcategories = list(category.subcategories.all())
    # 하위 카테고리를 하나 씩 까보면서 자식이 있으면 리스트에 추가
    for sub in category.subcategories.all():
        subcategories.extend(getsubcategories(sub))
    return subcategories

def showblog(request, blog_slug, category_slug=None):
    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    categories = BlogCategory.objects.filter(category_for=blog)

    # 카테고리 분류가 있는지 필터링
    if category_slug:
        # category_slug를 전달 받았을 때
        target_category = get_object_or_404(BlogCategory, slug=category_slug, category_for=blog)
        # all_categories: 목표 카테고리 리스트 + 반환된 카테고리 리스트를 합침.
        all_categories = [target_category] + getsubcategories(target_category)
        # 카테고리 id만 리스트로 뽑아냄.
        category_ids = [c.category_id for c in all_categories]
        # 반복 가능한 값 뒤에 __in 붙이면 django가 sql 쿼리로 변환해 줄 때 IN 조건으로 붙여준다.
        posts_query = PostContents.objects.filter(post_blog=blog, post_category__in=category_ids)
    else:
        # category_slug 없으면 블로그 전체 포스트 조회
        posts_query = PostContents.objects.filter(post_blog=blog)
    
    # 검색 쿼리가 있는지 필터링
    query = request.GET.get("q")
    if query:
        posts_query = posts_query.filter(post_title__icontains=query)
    # 필터링 된 포스트를 최신 날짜 순으로 정렬함.
    final_posts = posts_query.order_by('-post_date')

    # URL의 쿼리에서 'per_page' 파라미터 값 가져옴.
    posts_per_page = request.GET.get('per_page', 3)
    # 1. Paginator 객체를 생성합니다. (전체 포스트 리스트, 한 페이지당 보여줄 포스트 개수)
    paginator = Paginator(final_posts, posts_per_page)
    # 2. URL의 query string에서 'page' 값을 가져옵니다. 없으면 1페이지를 봅니다.
    page_number = request.GET.get('page', 1)
    
    # 3. 요청된 페이지에 해당하는 포스트 목록을 page_obj에 담습니다.
    # .get_page()는 존재하지 않는 페이지 번호 등 예외를 안전하게 처리해 줍니다.
    # 위에 수 많은 필터 구문때문에 실제로 여러 번 쿼리를 날릴 것 같지만, 
    # Django ORM이 즉시 수행하지 않고 마지막으로 데이터가 필요할 때(evaluate될 때) 한 번만 실행된다!
    page_obj = paginator.get_page(page_number)
    
    context = {
        'blog': blog,
        'posts': page_obj, 
        'categories': categories,
        'category_slug': category_slug,
    }
    
    return render(request, 'main/blog/blogpage.html', context)

def showpostdetail(request, blog_slug, post_slug):
    # blog 객체 가져오기
    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    # slug로 포스트 조회 (해당 블로그 소속인지도 확인)
    post = get_object_or_404(PostContents, slug=post_slug, post_blog=blog)
    # 포스트 카테고리 조회
    category = post.post_category
    # 댓글 목록 조회
    comments = PostComments.objects.filter(comment_post=post).order_by('comment_order', 'comment_date')

    # 댓글 폼 생성
    if request.user.is_authenticated:
        form = CommentForm(post=post, editor=request.user.bloginfo)
    else:
        form = None  # 비로그인 사용자는 폼 표시 안함

    context = {
        'blog': blog,
        'post': post, 
        'category': category, 
        'comments': comments,
        'form': form,
    }
    
    return render(request, 'main/blog/post/postdetail.html', context)

@login_required
def createpost(request):
    blog = get_object_or_404(BlogInfo, blog_user = request.user.id)
    if request.method=="POST":
        form = PostForm(request.POST, blog=blog)
        if form.is_valid():
            post = form.save(commit=False)
            try:
                # DB 트랜잭션으로 처리
                with transaction.atomic():
                    # 블로그 객체 연결
                    post.post_blog = blog
                    # uuid 앞 8자리로 생성
                    post.slug = str(uuid.uuid4())[:8]
                    post.save()
                    messages.success(request, "✅ 포스트를 작성했어요!")
                return redirect(showblog, blog_slug=blog.slug)  # 블로그 페이지로 이동
            except Exception as e:
                messages.error(request, f"🚨 이런.. 포스트 작성 중 오류가 발생했어요: {e}")    
                form = PostForm() # 실패 시 빈칸으로        
        else:
            print(form.errors)
            pass
    else: #Get 일 때
        form = PostForm(blog=blog)

    context = {
        'form': form,
    }

    return render(request, 'main/blog/post/editpost.html/', context)

@login_required
def editpost(request, blog_slug, post_slug):
    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    post = get_object_or_404(PostContents, slug=post_slug, post_blog=blog)

    if request.user != post.post_blog.blog_user:
        raise PermissionDenied("이 포스트를 수정할 권한이 없습니다.")
        messages.error(request, "❌ 이 포스트를 수정할 권한이 없습니다.")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    if request.method == 'POST':
        try:
            # DB 트랜잭션으로 처리
            with transaction.atomic():
                form = PostForm(request.POST, instance=post, blog=blog)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.post_editdate = timezone.now()
                    post.save()
                    messages.success(request, f"✅ \"{post.post_title}\" 글을 성공적으로 수정했어요!")
                return redirect('showpostdetail', blog_slug=blog.slug, post_slug=post.slug)
        except Exception as e:
                messages.error(request, f"🚨 이런.. 글 수정 중 오류가 발생했어요: {e}")    
                form = PostForm() # 실패 시 빈칸으로
                return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)
    else:
        form = PostForm(instance=post, blog=blog)
    return render(request, 'main/blog/post/editpost.html/', {'form': form})

@login_required
def deletepost(request, blog_slug, post_slug):
    # 블로그 및 포스트 가져오기
    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    targetpost = get_object_or_404(PostContents, slug=post_slug, post_blog=blog)

    # 작성자만 삭제 가능하도록
    if request.user != targetpost.post_blog.blog_user:
        raise PermissionDenied("이 포스트를 삭제할 권한이 없습니다.")
        messages.error(request, "❌ 이 포스트를 삭제할 권한이 없습니다.")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    if request.method == 'POST':
        try:
            # DB 트랜잭션으로 처리
            with transaction.atomic():
                # 댓글 삭제
                PostComments.objects.filter(comment_post=targetpost).delete()
                # 포스트 삭제
                targetpost.delete()
                print(f"삭제된 포스트: {targetpost.post_title}")
                messages.success(request, f"✅ \"{targetpost.post_title}\" 글을 성공적으로 삭제했어요!")
        except Exception as e:
                messages.error(request, f"🚨 이런.. 글 삭제 중 오류가 발생했어요: {e}")    
                form = PostForm() # 실패 시 빈칸으로
                return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)
    # 해당 블로그의 포스트 목록 페이지로 리다이렉트
    return redirect('showblog', blog_slug=blog.slug)

@login_required
def createcomment(request, blog_slug, post_slug):
    if request.method != 'POST':
        messages.error(request, "🚨 댓글 작성은 POST 방식으로만 가능합니다.")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    # blog, post 가져오기
    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    post = get_object_or_404(PostContents, slug=post_slug, post_blog=blog)

    # 수정 여부인지 확인
    comment_id = request.POST.get('comment_id')
    targetcomment = None

    # 부모 댓글 여부 확인 (답글인지)
    parent_comment_id = request.POST.get('parent_comment_id')
    parent_comment = None

    if comment_id:
        try:
            targetcomment = PostComments.objects.get(pk=comment_id)
        except PostComments.DoesNotExist:
            messages.error(request, "❌ 수정 대상 댓글이 존재하지 않습니다.")
            return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    if parent_comment_id:
        try:
            parent_comment = PostComments.objects.get(pk=parent_comment_id)
        except PostComments.DoesNotExist:
            messages.error(request, "❌ 답글 대상 댓글이 존재하지 않습니다.")
            return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    # 폼 생성
    form = CommentForm(
        request.POST,
        post=post,
        editor=request.user.bloginfo,
        parent_comment=parent_comment,
        comment_id=targetcomment,
    )

    try:
        with transaction.atomic():
            if form.is_valid():
                form.save()
                if parent_comment:
                    messages.success(request, "💬 답글이 등록되었습니다.")
                else:
                    messages.success(request, "✅ 댓글이 등록되었습니다.")
            else:
                messages.error(request, "🚨 댓글 작성 중 문제가 발생했습니다.")
                print(form.errors)
    except Exception as e:
        messages.error(request, f"🚨 댓글 등록 중 오류가 발생했습니다: {e}")

    return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

@login_required
def deletecomment(request, blog_slug, post_slug):
    if request.method != 'POST':
        messages.error(request, "🚨 삭제 요청은 POST 방식으로만 처리됩니다.")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    post = get_object_or_404(PostContents, slug=post_slug, post_blog=blog)

    # POST에서 comment_id 받아오기
    comment_id = request.POST.get('comment_id')
    if not comment_id:
        messages.error(request, "❌ 삭제할 댓글 ID가 전달되지 않았습니다.")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    comment_to_delete = get_object_or_404(PostComments, pk=comment_id)

    if comment_to_delete.comment_editor != request.user.bloginfo:
        messages.error(request, "❌ 댓글 작성자만 삭제할 수 있습니다.")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    try:
        with transaction.atomic():
            comment_to_delete.comment_isdelete = True
            comment_to_delete.save()
            messages.success(request, "🗑️ 댓글이 성공적으로 삭제되었습니다.")
    except Exception as e:
        messages.error(request, f"🚨 댓글 삭제 중 오류가 발생했어요: {e}")

    return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)
