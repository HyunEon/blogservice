from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models import PostComments, PostLike
from .models import Notification
from django.urls import reverse

# PostComments에 인스턴스가 post되면 발생함
@receiver(post_save, sender=PostComments)
def create_comment_notification(sender, instance, created, **kwargs):
    if not created:
        return

    # 답글이면 부모 댓글 작성자에게 알림.
    if instance.comment_isreply and instance.mention:
        recipient = instance.mention
        notif_type = 'reply'
        notif_message = f"{instance.comment_editor.blog_user.nickname}님이 답글을 남겼습니다."
    # 일반 댓글이면 글 작성자에게 알림.
    else:
        recipient = instance.comment_post.post_blog.blog_user
        notif_type = 'comment'
        notif_message = f"{instance.comment_editor.blog_user.nickname}님이 댓글을 남겼습니다."

    # 자기 자신에게는 안 보냄.
    if instance.comment_editor.blog_user == recipient:
        return

    # 포스트 자세히보기로 이동
    notification_url = reverse(
    'showpostdetail',
    kwargs={
        'blog_slug': instance.comment_post.post_blog.slug,
        'post_slug': instance.comment_post.slug
        }
    )

    # 알림 인스턴스 생성
    Notification.objects.create(
        notification_receiver=recipient,
        notification_sender=instance.comment_editor.blog_user,
        notification_type=notif_type,
        notification_message= notif_message,
        notification_url=notification_url
    )

# PostLike에 인스턴스가 post되면 발생함
@receiver(post_save, sender=PostLike)
def create_like_notification(sender, instance, created, **kwargs):
    if not created:
        return

    recipient = instance.like_post.post_blog.blog_user
    notif_type = 'like'

    # 자기 자신에게는 안 보냄.
    if instance.like_user == recipient:
        return

    # 포스트 자세히보기로 이동
    notification_url = reverse(
    'showpostdetail',
    kwargs={
        'blog_slug': instance.like_post.post_blog.slug,
        'post_slug': instance.like_post.slug
        }
    )

    # 알림 인스턴스 생성
    Notification.objects.create(
        notification_receiver=recipient,
        notification_sender=instance.like_user,
        notification_type=notif_type,
        notification_message=f"{instance.like_user.nickname}님이 좋아요를 남겼습니다.",
        notification_url=notification_url
    )