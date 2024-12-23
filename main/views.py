from django.shortcuts import render
from .models import MyModel

# Create your views here.
def showmain(request):
    return render(request, 'main/mainpage.html')

def showpost(request):
    post = MyModel.objects.first()

    context = {
        'post_title': post.post_title,
        'post_contents': post.post_contents,
    }
    
    return render(request, 'main/postpage.html', context=context)

