# Generated by Django 2.0.1 on 2018-01-26 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0007_auto_20180125_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='deployment',
            name='git_branch_text',
            field=models.CharField(default='master', max_length=100),
        ),
    ]
