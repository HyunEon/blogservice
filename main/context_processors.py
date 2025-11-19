from .models import BlogInfo, CustomUser, Notification # BlogInfo 모델을 가져옵니다.
from django.conf import settings

# settings에 정의한 구글 클라이언트 키를 가져옴.
def google_client_id(request):
    return {
        'GOOGLE_CLIENT_ID': getattr(settings, 'GOOGLE_CLIENT_ID', None)
    }

# 턴 스타일 키 가져옴.
def turnstile_keys(request):
    return {
        'TURNSTILE_SITE_KEY': getattr(settings, 'TURNSTILE_SITE_KEY', None)
    }

def user_blog_context(request):
    # 로그인한 사용자일 경우에만 실행
    if request.user.is_authenticated:
        try:
            # 현재 로그인한 사용자와 연결된 블로그 정보를 찾습니다.
            blog = BlogInfo.objects.get(blog_user=request.user)
            # 템플릿에서 'user_blog'라는 이름으로 blog 객체를 사용할 수 있게 됩니다.
            return {'user_blog': blog}
        except BlogInfo.DoesNotExist:
            # 사용자가 블로그를 가지고 있지 않은 경우
            return {'user_blog': None}
    
    # 로그인하지 않은 사용자의 경우
    return {'user_blog': None}

def notifications(request):
    if request.user.is_authenticated:
        return {
            'notifications': Notification.objects.filter(
                notification_receiver=request.user, notification_is_read=False
            ).order_by('-notification_created_at')[:5]  # 최근 5개만
        }
    return {}