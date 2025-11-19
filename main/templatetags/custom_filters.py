import urllib.parse
from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def urldecode(value):
    if value:
        return urllib.parse.unquote(value)
    return value

@register.filter
def timeago(value):
    now = timezone.now()
    diff = now - value

    seconds = diff.total_seconds()
    if seconds < 60:
        return "방금 전"
    elif seconds < 3600:
        return f"{int(seconds // 60)}분 전"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}시간 전"
    else:
        return f"{int(seconds // 86400)}일 전"