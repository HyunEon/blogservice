import os, requests, datetime, random, uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.text import slugify
from unidecode import unidecode
from main.models import BlogInfo, BlogCategory

User = get_user_model()

# 구글 소셜 계정 로그인 백엔드
class GoogleBackend:
    """
    Google 'idinfo'를 받아서 사용자를 인증, 생성, 반환하는 백엔드
    """
    def authenticate(self, request, idinfo=None):
        if not idinfo:
            return None

        email = idinfo.get("email")
        sub = idinfo.get("sub") # 구글 고유 ID

        if not email or not sub:
            return None # 인증에 필요한 정보가 없으면 실패

        try:
            # 기존 사용자인지 확인
            user = User.objects.get(username=sub)
            return user

        except User.DoesNotExist:
            # 신규 사용자 생성
            name = idinfo.get("name")
            profileimg = idinfo.get("picture")

            # get_or_create 대신 create 사용 (위에서 DoesNotExist로 확인했으므로)
            user = User.objects.create(
                username=sub,
                email=email,
                nickname=name,
                is_active=True, # 즉시 활성화
            )
            
            # 프로필 사진 다운로드
            try:
                resp = requests.get(profileimg, timeout=5)
                if resp.status_code == 200:
                    file_name = f"{name}-{uuid.uuid4()}.jpg"
                    user.profile_image.save(file_name, ContentFile(resp.content), save=False)
            except Exception as e:
                print("기본 프로필 이미지를 찾을 수 없습니다.")

            # 비밀번호 사용 불가 설정
            user.set_unusable_password()
            user.save() # 모든 변경사항 저장

            # 블로그, 카테고리 생성
            now = datetime.datetime.now()
            blog = BlogInfo.objects.create(
                blog_user=user,
                # G-{현재 초}-{랜덤 2자리} * {현재 ms}
                slug=f"G{now.second:02d}{(random.randint(10, 99) * (now.microsecond // 1000)):04d}"
            )
            BlogCategory.objects.create(
                category_name="내 글",
                category_for=blog,
                category_order=0,
                slug=slugify(unidecode("내 글")),
                parent=None 
            )
            return user

    def get_user(self, user_id):
        """
        세션에서 사용자를 꺼내올 때 사용되는 필수 메소드
        """
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None