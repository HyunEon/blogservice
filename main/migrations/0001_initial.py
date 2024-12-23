# Generated by Django 5.1.4 on 2024-12-23 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_title', models.CharField(db_index=True, help_text='블로그 포스트 제목 필드', max_length=20)),
                ('post_contents', models.TextField(help_text='블로그 포스트 내용 필드', null=True)),
            ],
        ),
    ]
