# Generated by Django 2.0.1 on 2018-01-25 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0003_deployment_webhook_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deployment',
            name='name_text',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]