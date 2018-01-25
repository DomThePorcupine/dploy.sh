from django.urls import path

from . import views

urlpatterns = [
    path('deployments/', views.index, name='index'),
    path('deployments/<int:deployment_id>/', views.detail, name='detail'),
    path('deployments/<int:deployment_id>/start/', views.start, name='start'),
    path('deployments/<int:deployment_id>/stop/',  views.stop,  name='stop'),
    path('deployments/<int:deployment_id>/build/', views.build, name='build'),
    path('deployments/<int:deployment_id>/delete/', views.delete, name='delete'),
    path('webhooks/<slug:deployment_hash>/', views.webhooks, name='webhook')
]