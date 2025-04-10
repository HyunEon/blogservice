# Generated by Django 5.1.4 on 2025-02-19 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_postcomments_comment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='postcomments',
            name='comment_isdelete',
            field=models.BooleanField(default=False, help_text='삭제 여부 확인'),
        ),
        migrations.AlterField(
            model_name='postcontents',
            name='post_category_for',
            field=models.CharField(help_text='카테고리 id', max_length=100),
        ),
    ]
