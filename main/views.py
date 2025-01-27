from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import PostContents, PostComments, BlogCategory
from .forms import CreatePostForm, CreateCommentForm
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
    posts = get_object_or_404(PostContents, post_id = post_id)
    comments = PostComments.objects.filter(comment_postadress = post_id).order_by('comment_order', 'comment_date')
    
    return render(request, 'main/postview.html', {'posts': posts, 'comments': comments})

def create_post(request):
    if request.method=="POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(showpost)
        else:
            print(form.errors)
    else: #Get 일 때
        form = CreatePostForm(initial={'category_id':'dddd', 'post_editor_uid': 'u192038', 'post_id': uuid.uuid4(), 'post_editdate': None})
    return render(request, 'main/editpost.html/', {'form': form})

def edit_post(request, post_id):
    targetpost = get_object_or_404(PostContents, post_id=post_id)

    if request.method == 'POST':
        form = CreatePostForm(request.POST, instance=targetpost)
        if form.is_valid():
            post = form.save(commit=False)
            post.post_editdate = timezone.now()
            form.save()
            return redirect(showpostdetail, post_id = post_id)
    else:
        form = CreatePostForm(instance=targetpost)
    
    return render(request, 'main/editpost.html', {'form': form})

def delete_post(request, post_id):
    targetpost = get_object_or_404(PostContents, post_id=post_id)
    if request.method == 'POST':
        targetpost.delete()
        return redirect(showpost)
    
    return render(request, 'main/postview.html', {'posts': targetpost})


def createcomment(request):
    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            form.save()
            #return redirect(showpostdetail(post_id))  # 성공 페이지로 리다이렉트
    else:
        form = CreateCommentForm(initial={'comment_id':uuid.uuid4(), 
                                          'comment_order': request.POST.get('comment_order'), 
                                          'comment_postadress': request.POST.get('comment_postadress'), 
                                          'comment_editor_uid': 'u192038',
                                          'comment_isreply': request.POST.get('comment_isreply'),
                                          'comment_replyto': request.POST.get('comment_replyto')})
    
        # 자바스크립트로 받는 데이터 중에 프론트 단에서 악의적으로 수정할 수 있으니 서버단에서 유효성 검사를 추가해야 함
        
    return render(request, 'main/postview.html/', {'form': form})

