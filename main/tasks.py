from celery import shared_task
from io import BytesIO
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from PIL import Image
import requests, uuid
from django.db.models import F

'''
celery -A blog_project worker -l info
'''
@shared_task
# 썸네일 생성 로직, webP로 인코딩 후 저장함.
def generate_thumbnail_async(post_id):
    try:
        # 지연 임포트: Celery가 worker에서 models를 먼저 로딩하려다 Django 앱 초기화 순서 때문에 순환 import가 발생하므로 이를 방지하기 위해 함수 안에 선언함.
        from main.models import PostContents
        post = PostContents.objects.get(pk=post_id)
        if post.post_thumbnail:
            return  # 이미 썸네일이 있으면 패스

        soup = BeautifulSoup(post.post_contents, "html.parser")
        img_tag = soup.find("img")
        if not img_tag:
            return

        img_url = img_tag.get("src")
        response = requests.get(img_url, timeout=5)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))
        img.thumbnail((400, 300))

        buffer = BytesIO()
        img.save(
            buffer,
            format="WEBP",
            quality=80,
            method=6,
            icc_profile=img.info.get("icc_profile") if "icc_profile" in img.info else None
        )
        buffer.seek(0)

        filename = f"thumb_{uuid.uuid4().hex}.webp"
        post.post_thumbnail.save(filename, ContentFile(buffer.getvalue()), save=True)
        print(f"[Celery] 썸네일 생성 완료: {filename}")

    except Exception as e:
        print(f"[Celery Error] {e}")

@shared_task
# 조회수 증가 로직
def increase_post_view_count(post_id):
    try:
        from main.models import PostContents
        # F를 붙이면 DB 단에서 직접 처리함
        PostContents.objects.filter(pk=post_id).update(
            post_view_count=F('post_view_count') + 1
        )
        print("[Celery] 조회수 증가 완료")
    except Exception as e:
        print(f"[Celery Error] {e}")