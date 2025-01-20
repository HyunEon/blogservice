from django.shortcuts import render, redirect
from .models import PostContents, PostComments, BlogCategory
from .forms import CreatePostForm
import uuid

# Create your views here.
def showmain(request):
    return render(request, 'main/mainpage.html/')

def showpost(request):
    categorys = BlogCategory.objects.all() # 나중에 블로그 id로 필터링 걸어서 가져오기
    posts = PostContents.objects.all()
    comments = PostComments.objects.all()

    return render(request, 'main/postpage.html/', {'posts': posts, 'comments': comments, 'categorys': categorys})

def showeditpost(request):
    if request.method=="POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(showpost)
        else:
            print(form.errors)
    else: #Get 일 때
        form = CreatePostForm(initial={'category_id':'dddd', 'post_editor_uid': 'u192038', 'post_id': uuid.uuid4()})
    return render(request, 'main/editpost.html/', {'form': form})