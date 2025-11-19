from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.core.cache import cache
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
from django.db.models import Q, Max, Min, F
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
from .models import BlogInfo, PostContents, PostComments, BlogCategory, Notification, PostLike
from .forms import PostForm, CommentForm, RegisterForm, UserUpdateForm, BlogUpdateForm, CategoryForm
from unidecode import unidecode
import uuid, os, re, random, json, requests, datetime, traceback
from django.views.decorators.http import require_POST
from main.tasks import increase_post_view_count

from google.oauth2 import id_token
from google.auth.transport import requests as grequests

from mptt.exceptions import InvalidMove
from mptt.forms import MoveNodeForm

User = get_user_model()
# Create your views here.

# 클라이언트 IP 가져오기
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # 여러 IP가 콤마로 넘어올 경우 첫 번째가 클라이언트 IP
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

# Cloudflare turnstile 검증
def validate_turnstile(token, secret, remoteip=None):
    url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

    data = {
        'secret': secret,
        'response': token
    }

    if remoteip:
        data['remoteip'] = remoteip

    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Turnstile validation error: {e}")
        return {'success': False, 'error-codes': ['internal-error']}

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
                        category_name="내 글",
                        category_for=blog,
                        category_sort_order=0,
                        slug=slugify(unidecode("내 글")),
                        parent=None  # 최상위 카테고리면 None
                    )
                    # django message - https://docs.djangoproject.com/en/5.0/ref/contrib/messages/
                messages.success(request, " 회원가입이 완료되었어요!")
                return redirect(loginview)  # 가입 후 로그인 페이지 등으로 이동
            except Exception as e:
                messages.error(request, f"((((；゜Д゜))) 회원가입 중 오류가 발생했어요!: {e}")
    else:
        form = RegisterForm()
    return render(request, "main/register.html", {"form": form})

# Google 회원가입/로그인, 기존 Django 세션과 연동에 문제가 있어, Custom 세션 사용.
@csrf_exempt
def googlelogin(request):
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

    except ValueError as e:
        print("GOOGLE LOGIN ERROR:", str(e))
        traceback.print_exc()
        return HttpResponseBadRequest(f"Invalid token: {str(e)}")

    # authenticate 호출 (idinfo를 전달)
    # Django는 settings.AUTHENTICATION_BACKENDS를 순회하며
    # idinfo를 받는 authenticate 메소드를 찾아 실행합니다.
    user = authenticate(request, idinfo=idinfo) 

    if user is not None:
        # authenticate가 성공하면 user 객체에 .backend 속성이 자동으로 붙음
        login(request, user) 
        messages.success(request, f" {user.nickname}님, 환영합니다 😊")
        # 메인으로
        return redirect('/')
    else:
        # 인증 실패
        messages.error(request, "로그인에 실패했습니다. 유효하지 않은 사용자입니다.")
        return redirect(loginview)

def loginview(request):
    # 이미 로그인 되어 있으면 main으로 리다이렉트
    if request.user.is_authenticated:
        return redirect(showmain)

    # 로그인 요청 시
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # 폼이 유효하면 Turnstile 검증 시작
            token = request.POST.get("cf-turnstile-response")
            result = validate_turnstile(
                token,
                secret=settings.TURNSTILE_SECRET_KEY, 
                remoteip=get_client_ip(request)
            )
            print(result)

            if not result.get("success", False):
                messages.error(request, "보안 인증 검증에 실패했어요")
                form = AuthenticationForm(request, data=request.POST)
                return render(request, 'main/login.html', {'form': form, 'TURNSTILE_SITE_KEY': settings.TURNSTILE_SITE_KEY})
            # 폼이 유효하면 사용자를 로그인시키고 메인 페이지로 리다이렉트
            user = form.get_user()
            login(request, user)
            messages.success(request, f" {user.nickname}님, 환영합니다 😊")
            # 사용자가 보고 있던 페이지가 있으면 해당 페이지로 리디렉트, 없으면 메인으로
            next_url = request.GET.get('next') or request.POST.get('next') or '/'
            return redirect(next_url)
    else:
    # GET 요청이면 빈 로그인 폼을 보여줌
        form = AuthenticationForm()
    context = {
        'form': form,
        'TURNSTILE_SITE_KEY': settings.TURNSTILE_SITE_KEY,
    }
    return render(request, 'main/login.html', context)

@login_required
def logoutview(request):
    logout(request)
    messages.info(request, "로그아웃 했어요! 다음에 또 봐요 👋")
    return redirect(showmain)

def showmain(request):
    user = request.user

    # 메시지가 있으면 캐시 사용 안 함
    if messages.get_messages(request):
        return render(request, "main/mainpage.html", {
            "bloglist": BlogInfo.objects.order_by('-blog_created_date')[:3],
            "postlist": PostContents.objects.order_by('-post_date'),
        })

    # 비로그인 사용자 대상
    if not user.is_authenticated:
        # 포스트 슬러그 값 키로 사용
        key = "page:main"

        cached = cache.get(key)
        if cached:
            return cached

    # 추천 블로그 3개 가져옴, 추후 첫 블로그와 마지막 블로그 인덱스 값을 가져와 랜덤한 값을 생성하는 로직을 적용
    bloglist = BlogInfo.objects.all().filter().order_by('-blog_created_date')[:3]
    postlist = PostContents.objects.filter().order_by('-post_date')

    response = render(request, "main/mainpage.html", {
        "bloglist": bloglist,
        "postlist": postlist,
    })
    
    # 응답을 캐시에 저장함, 총 5분 캐싱
    if not user.is_authenticated:
        cache.set(key, response, 60 * 5)

    return response

@login_required
def settingspage(request):
    tab = request.GET.get('tab', 'profile')
    blog = get_object_or_404(BlogInfo, blog_user=request.user)

    if tab == 'profile':
        if request.method == 'POST':
            form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "프로필을 멋지게 수정했어요!")
                return redirect(f'{reverse("settingspage")}?tab=profile')
        else:
            form = UserUpdateForm(instance=request.user)
            context = {'form': form, 'tab': tab}
    elif tab == 'blog':
        if request.method == 'POST':
            form = BlogUpdateForm(request.POST, instance=blog)
            if form.is_valid():
                form.save()
                messages.success(request, "블로그 정보를 저장했어요!")
                return redirect(f'{reverse("settingspage")}?tab=blog')
        else:
            form = BlogUpdateForm(instance=blog)
            context = {'form': form, 'tab': tab}
    elif tab == 'category':
        blog = get_object_or_404(BlogInfo, blog_user=request.user)
        categories = BlogCategory.objects.filter(category_for=blog)
        form = CategoryForm()

        context = {
        'form': form,
        'tab': 'category',
        'categories': categories
    }

    return render(request, 'main/settings/settings.html', context)

# 카테고리 생성
@login_required
def createcategory(request):
    blog = get_object_or_404(BlogInfo, blog_user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.category_for = blog
            # 제일 왼쪽 트리 정렬로 마지막 루트 카테고리를 찾음
            last_root = BlogCategory.objects.filter(category_for=blog, parent__isnull=True ).order_by('-tree_id', '-lft').first() 
            # 마지막 루트 카테고리를 찾았으면 오른쪽 정렬한 후 저장
            if last_root:
                category.insert_at(last_root, position='right', save=True)
            else:
                # 카테고리가 아무 것도 없는 환경이면 그냥 저장
                category.save()
            category.save()
            # Ajax 요청이면 JSON 반환
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': category.category_id,
                    'name': category.category_name
                })
            return redirect(settingspage)

# 카테고리 업데이트
@login_required
def updatecategory(request, category_id):
    if request.method == "POST":
        name = request.POST.get("name")
        try:
            category = BlogCategory.objects.get(pk=category_id)
            category.category_name = name
            category.save()
            return JsonResponse({"success": True, "id": str(category.category_id), "name": category.category_name})
        except Category.DoesNotExist:
            return JsonResponse({"success": False, "error": "Not found"}, status=404)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

# 카테고리 삭제
@login_required
def deletecategory(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(BlogCategory, pk=category_id)
        blog = category.category_for  # 카테고리가 속한 블로그

        # 블로그에 남아있는 카테고리 수 확인
        remaining_count = BlogCategory.objects.filter(category_for=blog).count()
        if remaining_count <= 1:
            messages.error(request, "마지막 카테고리는 삭제할 수 없어요!")
            return redirect(f'{reverse("settingspage")}?tab=category')
            
        try:
            category.delete()
            messages.success(request,'카테고리를 삭제했어요!')
        except Exception as e:
            messages.error(request, f'((((；゜Д゜))) 카테고리 삭제에 실패했어요..: {e}')
    return redirect(f'{reverse("settingspage")}?tab=category')

# 카테고리 정렬은 ajax를 통한 비동기 방식으로 진행, crud는 form을 통한 방식으로
@require_POST
@login_required
@transaction.atomic # 모든 변경이 성공하거나 실패하도록 트랜잭션 처리
def reordercategory(request):
    try:
        data = json.loads(request.body)
        
        # 재귀 함수를 사용하여 모든 노드의 부모와 순서를 업데이트함
        def update_nodes(nodes_data, parent=None):
            for i, node_data in enumerate(nodes_data):
                pk = node_data['id']
                try:
                    category = BlogCategory.objects.get(category_id=pk)
                except BlogCategory.DoesNotExist:
                    # 예외 처리: 존재하지 않는 ID가 오면 무시
                    continue

                # 부모 및 순서 필드 업데이트 (저장은 아직 안 함)
                category.parent = parent
                category.category_order = i  # 1단계에서 만든 'order' 필드
                
                # save()는 MPTT가 아닌 일반 모델 필드만 업데이트하도록 'update_fields' 사용
                # MPTT 필드(lft, rght)는 나중에 rebuild()가 처리합니다.
                category.save(update_fields=['parent', 'category_order'])

                # 이 노드의 자식 노드들에 대해 재귀 호출
                if 'children' in node_data:
                    update_nodes(node_data['children'], parent=category)

        # JSON 데이터의 최상위 레벨부터 재귀 시작
        update_nodes(data, parent=None)
        # 모든 'parent'와 'order' 필드가 업데이트된 후, rebuild()를 호출하여 lft, rght, level, tree_id를 재계산
        BlogCategory.objects.rebuild()
        # 성공하면 204 반환
        return HttpResponse(status=204)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def showblog(request, blog_slug, category_slug=None):
    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    categories = BlogCategory.objects.filter(category_for=blog).order_by('tree_id', 'lft')
    total_posts_count = PostContents.objects.filter(post_blog=blog).count()

    # 카테고리 분류가 있는지 필터링
    if category_slug:
        # category_slug를 전달 받았을 때
        target_category = get_object_or_404(BlogCategory, slug=category_slug, category_for=blog)
        # 카테고리 id만 리스트로 뽑아냄.
        category_ids = target_category.get_descendants(include_self=True).values_list('category_id', flat=True)
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
        'totalposts': total_posts_count,
        'category_slug': category_slug,
    }
    
    return render(request, 'main/blog/blogpage.html', context)

def showpostdetail(request, blog_slug, post_slug):
    user = request.user
    # blog 객체 가져오기
    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    # slug로 포스트 조회 (해당 블로그 소속인지도 확인)
    post = get_object_or_404(PostContents, slug=post_slug, post_blog=blog)
    # 조회수 증가, Celery Worker로 비동기 처리 & 캐시 앞 단에서 둬서 캐싱되기 전에 처리
    increase_post_view_count.delay(post.post_id)
    # 로그인하지 않은 사용자만 캐싱함: 로그인한 사용자는 포스트 또는 댓글에 대한 CRUD 동작이 있으므로 캐싱하면 안됨.
    if not user.is_authenticated:
        # 포스트 슬러그 값 키로 사용
        key = f"page:post:{post_slug}"
        cached = cache.get(key)
        if cached:
            return cached

    
    # 좋아요 조회 : 있으면 가져옴
    if request.user.is_authenticated: 
        liked = PostLike.objects.filter(like_user=request.user, like_post=post).exists()
    else:
        liked = PostLike.objects.filter(like_post=post).exists()
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
        'liked': liked,
        'category': category, 
        'comments': comments,
        'form': form,
    }

    response = render(request, 'main/blog/post/postdetail.html', context)

    if not user.is_authenticated:
        cache.set(key, response, 60 * 10)  # 포스트 상세 페이지는 10분간 캐싱

    return response

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
                    messages.success(request, "포스트를 작성했어요!")
                return redirect(showblog, blog_slug=blog.slug)  # 블로그 페이지로 이동
            except Exception as e:
                messages.error(request, f"((((；゜Д゜))) 포스트 작성 중 오류가 발생했어요: {e}")    
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
        messages.error(request, "이 포스트를 수정할 권한이 없어요!")
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
                    messages.success(request, f" \"{post.post_title}\"글을 수정했어요!")
                return redirect('showpostdetail', blog_slug=blog.slug, post_slug=post.slug)
        except Exception as e:
                messages.error(request, f"((((；゜Д゜))) 글 수정 중 오류가 발생했어요: {e}")    
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
        messages.error(request, "이 포스트를 삭제할 권한이 없어요!")
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
                messages.success(request, f" \"{targetpost.post_title}\" 글을 삭제했어요!")
        except Exception as e:
                messages.error(request, f"((((；゜Д゜))) 글 삭제 중 오류가 발생했어요: {e}")    
                form = PostForm() # 실패 시 빈칸으로
                return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)
    # 해당 블로그의 포스트 목록 페이지로 리다이렉트
    return redirect('showblog', blog_slug=blog.slug)

@login_required
def createcomment(request, blog_slug, post_slug):
    if request.method != 'POST':
        messages.error(request, "올바르지 않은 요청입니다.")
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
            messages.error(request, "흠? 수정할 댓글이 존재하지 않네요..")
            return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    if parent_comment_id:
        try:
            parent_comment = PostComments.objects.get(pk=parent_comment_id)
        except PostComments.DoesNotExist:
            messages.error(request, "흠? 답글을 달 댓글이 존재하지 않네요..")
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
                    messages.success(request, "답글을 등록했어요!")
                else:
                    messages.success(request, "댓글을 등록했어요!")
            else:
                messages.error(request, "((((；゜Д゜))) 댓글 작성 중 문제가 발생했습니다.")
                print(form.errors)
    except Exception as e:
        messages.error(request, f"((((；゜Д゜))) 댓글 등록 중 오류가 발생했어요: {e}")

    return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

@login_required
def deletecomment(request, blog_slug, post_slug):
    if request.method != 'POST':
        messages.error(request, "올바르지 않은 요청입니다.")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    blog = get_object_or_404(BlogInfo, slug=blog_slug)
    post = get_object_or_404(PostContents, slug=post_slug, post_blog=blog)

    # POST에서 comment_id 받아오기
    comment_id = request.POST.get('comment_id')
    if not comment_id:
        messages.error(request, "올바르지 않은 요청입니다.")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    comment_to_delete = get_object_or_404(PostComments, pk=comment_id)

    if comment_to_delete.comment_editor != request.user.bloginfo:
        messages.error(request, "댓글 작성자만 삭제할 수 있어요!")
        return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

    try:
        with transaction.atomic():
            comment_to_delete.comment_isdelete = True
            comment_to_delete.save()
            messages.success(request, "댓글을 삭제했어요!")
    except Exception as e:
        messages.error(request, f"((((；゜Д゜))) 댓글 삭제 중 오류가 발생했어요: {e}")

    return redirect('showpostdetail', blog_slug=blog_slug, post_slug=post_slug)

@login_required
def notificationlist(request):
    # 로그인한 사용자의 알림 가져오기
    notifications = Notification.objects.filter(notification_receiver=request.user, notification_is_read=False).order_by('-notification_created_at')
    return render(request, 'main/notification.html/', {'notifications': notifications})

@login_required
def notificationread(request):
    # 알림 읽음 처리
    try:
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])
            
        if not notification_ids:
            return JsonResponse({'status': 'failed', 'message': 'No notification IDs provided'}, status=400)
        # 요청한 사용자가 해당 알림에 속한 사용자인지 확인
        target_notifications = Notification.objects.filter(notification_receiver=request.user, id__in=notification_ids)
        # 일괄 읽음 표시
        updated_count = target_notifications.update(notification_is_read=True)

    except json.JSONDecodeError:
        return JsonResponse({'status': 'failed', 'message': 'Invalid JSON format'}, status=400)
    except Exception as e:
        print(f"Error updating notifications: {e}")
        return JsonResponse({'status': 'failed', 'message': 'Server error during update'}, status=500)
    # 성공 응답
    return JsonResponse({'status': 'success', 'message': f'{updated_count} notifications marked as read'})

@login_required
def togglelike(request, post_id):
    post = get_object_or_404(PostContents, post_id=post_id)
    # 새로 created 되면 True, 이미 created된 상태면 False를 반환함.
    like, created = PostLike.objects.get_or_create(like_user=request.user, like_post=post)
    if not created:
        # 이미 좋아요 되어 있으면 취소
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})