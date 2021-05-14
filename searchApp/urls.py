from django.urls import path
from searchApp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('song/<int:songid>/', views.song, name='song'),
]