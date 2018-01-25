from django.urls import path

from . import views

urlpatterns = [
    path('', views.userlogin, name='login'),
]