from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.http import Http404
from django.db.models import Q
from .models import BlogInfo, PostContents, PostComments, BlogCategory
from .forms import PostForm, CommentForm
import uuid, os, re

# Create your views here.
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
            return redirect(showmain)
    else:
    # GET 요청이면 빈 로그인 폼을 보여줌
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

@login_required
def logoutview(request):
    logout(request)
    return redirect(showmain)

@login_required
def showmain(request):
    '''if request.user.is_authenticated:
        return render(request, 'main/mainpage.html')'''
    return render(request, 'main/mainpage.html')

@login_required
def showpost(request):
    user_id = request.user.id
    blog = get_object_or_404(BlogInfo, blog_user = user_id).blog_id
    categorys = BlogCategory.objects.all().filter(category_for = blog)
    query = request.GET.get("q", None)

    if query:
        posts = PostContents.objects.filter(post_title__icontains=query).order_by('-post_date')  # 대소문자 구분 없이 검색
    else:
        posts = PostContents.objects.all().order_by('-post_date')  # 전체 포스트 가져오기

    return render(request, 'main/postpage.html/', {'posts': posts, 'categorys': categorys})

@login_required
def showpostbycategory(request, category_id):
    user_id = request.user.id
    blog = get_object_or_404(BlogInfo, blog_user = user_id).blog_id
    # 카테고리 란에 들어갈 카테고리를 리턴해 줌, 어떤 포스트를 보든 표시되어야 하기 때문에 반드시 필요함
    categorys = BlogCategory.objects.all().filter(category_for = blog)
    # 해당 카테고리의 하위 카테고리가 있다면 가져와서 ID만 잘라냄, Q객체를 사용해서 OR 조건을 표기할 수 있음
    target_categories = BlogCategory.objects.all().filter(Q(category_id = category_id) | Q(category_depth_for = category_id)).values_list('category_id', flat=True)
    posts = PostContents.objects.all().filter(post_category_for__in = target_categories).order_by('-post_date') # 작성된 날짜 순으로 정렬

    return render(request, 'main/postpage.html/', {'posts': posts, 'categorys': categorys})

@login_required
def showpostdetail(request, post_id):
    #posts = PostContents.objects.get(PostContents, post_id = target_post_id)
    post = get_object_or_404(PostContents, post_id = post_id)
    category = get_object_or_404(BlogCategory, category_id = post.post_category_for)
    comments = PostComments.objects.filter(comment_postadress = post_id).order_by('comment_order', 'comment_date')
    
    return render(request, 'main/postview.html', {'post': post, 'category': category, 'comments': comments})

@login_required
def create_post(request):
    user_id = request.user.id
    blog_id = get_object_or_404(BlogInfo, blog_user = user_id).blog_id # 더미 데이터
    categories = BlogCategory.objects.all().filter(category_for = blog_id)

    if request.method=="POST":
        form = PostForm(request.POST)
        form.data = form.data.copy()
        form.data['post_id'] = uuid.uuid4()
        form.data['post_editor_uid'] = user_id
        #form.data['post_editdate'] = None

        if form.is_valid():
            post = form.save(commit=False) # 폼 임시 저장
            post.save()
            return redirect(showpost)
        else:
            print(form.errors)
            form = PostForm() # 유효성 검사 실패 시 빈칸으로
    else: #Get 일 때
        form = PostForm()
    return render(request, 'main/editpost.html/', {'form': form, 'categories': categories})

@login_required
def edit_post(request, post_id):
    user_id = request.user.id
    blog_id = get_object_or_404(BlogInfo, blog_user = user_id).blog_id
    categories = BlogCategory.objects.all().filter(category_for = blog_id)
    targetpost = get_object_or_404(PostContents, post_id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=targetpost)
        # 폼에서 id와 editor_uid를 필수로 지정했기 때문에 해당 필드들을 다시 입력해준다
        form.data = form.data.copy()
        form.data['post_id'] = targetpost.post_id
        form.data['post_editor_uid'] = targetpost.post_editor_uid

        if form.is_valid():
            post = form.save(commit=False)
            post.post_editdate = timezone.now()
            post.save()
            return redirect(showpostdetail, post_id = post_id)
        else:
            print(form.errors)
    else:
        form = PostForm(instance=targetpost)
    
    return render(request, 'main/editpost.html', {'form': form, 'categories': categories})

@login_required
def delete_post(request, post_id):
    targetpost = get_object_or_404(PostContents, post_id=post_id)

    if request.method == 'POST':

        # 포스트에 삽입된 이미지 삭제 로직
        media_root = settings.MEDIA_ROOT
        image_urls = re.findall(r'\/uploads\/[^\s\'\"]+', targetpost.post_contents)
        
        print("Extracted Image URL:", image_urls)

        for url in image_urls:
            image_path = os.path.join(media_root, url.lstrip('/'))
            print("Path:", image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
            else:
                print(f"Image not found: {image_path}")
        
        # 포스트에 달린 댓글 삭제
        PostComments.objects.all().filter(comment_postadress = post_id).delete()

        # 포스트 삭제
        targetpost.delete()

        return redirect(showpost)
    
    return render(request, 'main/postview.html', {'posts': targetpost})

@login_required
def createcomment(request, post_id):
    user_id = request.user.id
    # 댓글이 없는 글이면 order는 0부터 시작, 있으면 마지막 댓글 order + 1
    try:
        targetpostcomment = PostComments.objects.all().filter(comment_postadress=post_id).latest('comment_date')
        comment_order = targetpostcomment.comment_order + 1
    except PostComments.DoesNotExist:
        comment_order = 0

    if request.method == 'POST':
        form = CommentForm(request.POST)
        form.data = form.data.copy()
        form.data['comment_id'] = uuid.uuid4()
        form.data['comment_editor_uid'] = user_id
        form.data['comment_postadress'] = post_id
        form.data['comment_order'] = comment_order

        if form.is_valid():
            form.save()
            # reverse 함수를 써서 url에 파라미터를 넣어 리다이렉트 할 수 있었다..
            return redirect(reverse('showpostdetail', args=[post_id])) # 성공 페이지로 리다이렉트
        else:
            print(form.errors)
    else:
        form = CommentForm()
        
    return render(request, 'main/postview.html/', {'form': form, 'post_id': post_id})

# 답글 작성하는 view
@login_required
def createreplycomment(request, post_id, comment_id):
    user_id = request.user.id
    # 해당 댓글의 마지막 댓글 order를 가져옴
    try:
        targetpostcomment = PostComments.objects.all().filter(comment_postadress = post_id, comment_id = comment_id).latest('comment_date')
        comment_order = targetpostcomment.comment_order
    except:
        raise Http404("The comment does not exist.")

    if request.method == 'POST':
        form = CommentForm(request.POST)
        form.data = form.data.copy()
        form.data['comment_id'] = uuid.uuid4()
        form.data['comment_editor_uid'] = user_id
        form.data['comment_postadress'] = post_id
        form.data['comment_order'] = comment_order
        form.data['comment_isreply'] = True
        form.data['comment_replyto'] = comment_id

        if form.is_valid():
            form.save()
            # reverse 함수를 써서 url에 파라미터를 넣어 리다이렉트 할 수 있었다..
            return redirect(reverse('showpostdetail', args=[post_id])) # 성공 페이지로 리다이렉트
        else:
            print(form.errors)
    else:
        form = CommentForm()
        
    return render(request, 'main/postview.html/', {'form': form, 'post_id': post_id})

@login_required
def deletecomment(request, post_id, comment_id):
    targetcomment = get_object_or_404(PostComments, comment_id = comment_id)

    # 댓글 삭제의 경우, 내용 및 옵션 변경 처리/ 추후 관련 댓글까지 모두 삭제하도록 하는 것이 더 나을지 고민해봐야겠다
    if request.method == 'POST':
        targetcomment.comment_contents = "삭제된 댓글입니다."
        targetcomment.comment_isdelete = True
        targetcomment.save()
        return redirect(reverse('showpostdetail', args=[post_id])) # 성공 페이지로 리다이렉트
    
    return redirect(reverse('showpostdetail', args=[post_id]))