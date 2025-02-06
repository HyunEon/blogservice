from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import BlogInfo, PostContents, PostComments, BlogCategory
from .forms import PostForm, CommentForm
import uuid

# Create your views here.
def showmain(request):
    return render(request, 'main/mainpage.html/')

def showpost(request):
    categorys = BlogCategory.objects.all() # 나중에 블로그 id로 필터링 걸어서 가져오기
    posts = PostContents.objects.all().order_by('-post_date') # 작성된 날짜 순으로 정렬

    return render(request, 'main/postpage.html/', {'posts': posts, 'categorys': categorys})

def showpostdetail(request, post_id):
    #posts = PostContents.objects.get(PostContents, post_id = target_post_id)
    post = get_object_or_404(PostContents, post_id = post_id)
    category = get_object_or_404(BlogCategory, category_id = post.post_category_for)
    comments = PostComments.objects.filter(comment_postadress = post_id).order_by('comment_order', 'comment_date')
    
    return render(request, 'main/postview.html', {'post': post, 'category': category, 'comments': comments})

def create_post(request):
    blog_id = get_object_or_404(BlogInfo, blog_user ='u192038').blog_id # 더미 데이터
    categories = BlogCategory.objects.all().filter(category_for = blog_id)

    if request.method=="POST":
        form = PostForm(request.POST)
        form.data = form.data.copy()
        form.data['post_id'] = uuid.uuid4()
        form.data['post_editor_uid'] = 'u192038'
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

def edit_post(request, post_id):
    blog_id = get_object_or_404(BlogInfo, blog_user ='u192038').blog_id # 더미 데이터
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

def delete_post(request, post_id):
    targetpost = get_object_or_404(PostContents, post_id=post_id)
    if request.method == 'POST':
        targetpost.delete()
        return redirect(showpost)
    
    return render(request, 'main/postview.html', {'posts': targetpost})

def createcomment(request, post_id):
    targetpostcomment = get_object_or_404(PostComments, comment_postadress=post_id)
    print(targetpostcomment)

    # todo: 댓글 뷰도 동일한 방식으로 처리하기, 폼을 사용 안 하는게 수월할지도 모르겠음
    if request.method == 'POST':
        form = CommentForm(request.POST)
        form.data = form.data.copy()
        form.data['comment_id'] = uuid.uuid4()
        form.data['comment_editor_uid'] = 'u192038'
        form.data['comment_postadress'] = post_id
        form.data['comment_order'] = targetpostcomment.comment_order + 1

        if form.is_valid():
            print(form)
            #form.save()
            return redirect(showpostdetail(post_id))  # 성공 페이지로 리다이렉트
        else:
            print(form.errors)
    else:
        form = CommentForm()
        
    return render(request, 'main/postview.html/', {'form': form})

