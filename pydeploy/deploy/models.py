"""
This module contains our deployment model
"""
from django.db import models


# Create your models here.
class Deployment(models.Model):
    """
    This is our only custom class for this project
    it is very simple and holds all the generic info
    you would need when doing dev ops manually
    """
    name_text = models.CharField(max_length=100, unique=True)
    git_url_text = models.CharField(max_length=250)
    dir_text = models.CharField(max_length=250)
    is_running = models.BooleanField(default=False)
    webhook_text = models.CharField(max_length=100, default='')
    container_id_text = models.CharField(max_length=100, default='')
    container_port = models.CharField(max_length=5, default='')
    local_port = models.CharField(max_length=5, default='')
    # NOTE we default to master if we are not given a branch
    git_branch_text = models.CharField(max_length=100, default='master')
    domain_text = models.CharField(max_length=200, default='')
    is_compose = models.BooleanField(default=False)

    def __str__(self):
        return self.name_text
