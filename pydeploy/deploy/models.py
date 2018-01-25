from django.db import models

# Create your models here.
class Deployment(models.Model):
  name_text = models.CharField(max_length=100, unique=True)
  git_url_text = models.CharField(max_length=250)
  dir_text = models.CharField(max_length=250)
  is_running = models.BooleanField(default=False)
  webhook_text = models.CharField(max_length=100,default='')
  container_id_text = models.CharField(max_length=100, default='')
  container_port = models.CharField(max_length=5, default='')
  local_port = models.CharField(max_length=5, default='')
  def __str__(self):
    return self.name_text