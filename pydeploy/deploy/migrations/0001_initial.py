# Generated by Django 2.0.1 on 2018-01-24 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('name_text', models.CharField(max_length=100)),
                ('git_url_text', models.CharField(max_length=250)),
                ('dir_text', models.CharField(max_length=250)),
            ],
        ),
    ]