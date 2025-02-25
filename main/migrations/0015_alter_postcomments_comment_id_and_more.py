# Generated by Django 5.1.4 on 2025-01-27 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_postcomments_comment_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postcomments',
            name='comment_id',
            field=models.CharField(help_text='댓글 id 형식은 GUID', max_length=100),
        ),
        migrations.AlterField(
            model_name='postcomments',
            name='comment_order',
            field=models.IntegerField(default=1, help_text='댓글/대댓글을 정렬하기 위한 순서이자 묶어주기 위한 그룹 대댓글의 경우 같은 order로 묶고 생성 날짜로 정렬한다'),
        ),
        migrations.AlterField(
            model_name='postcomments',
            name='comment_replyto',
            field=models.CharField(blank=True, help_text='답글 주소 id, 댓글 ID를 여기다 넣음, 근데 order 스키마로 충분한 것 같아 제거해야 하나 고민중', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='postcontents',
            name='post_editdate',
            field=models.DateTimeField(help_text='블로그 포스트 수정된 날짜', null=True),
        ),
    ]
