# Generated by Django 2.0.1 on 2018-01-25 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0006_auto_20180125_1107'),
    ]

    operations = [
        migrations.AddField(
            model_name='deployment',
            name='container_port',
            field=models.CharField(default='', max_length=5),
        ),
        migrations.AddField(
            model_name='deployment',
            name='local_port',
            field=models.CharField(default='', max_length=5),
        ),
    ]