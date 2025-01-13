from django.shortcuts import render, redirect
from .models import PostContents, PostComments
from .forms import CreatePostForm
import uuid

# Create your views here.
def showmain(request):
    return render(request, 'main/mainpage.html/')

def showpost(request):
    posts = PostContents.objects.all()
    comments = PostComments.objects.all()

    return render(request, 'main/postpage.html/', {'posts': posts, 'comments': comments})

def showeditpost(request):
    if request.method=="POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(showpost)
        else:
            print(form.errors)
    else: #Get 일 때
        form = CreatePostForm(initial={'post_editor_uid': 'u192038', 'post_id': uuid.uuid4()})
    return render(request, 'main/editpost.html/', {'form': form})