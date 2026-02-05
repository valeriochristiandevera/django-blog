from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('post/<slug:slug>/', views.post_detail_view, name='post_detail'),
    path('post/create/', views.post_create_view, name='post_create'),
    path('post/<slug:slug>/edit/', views.post_edit_view, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete_view, name='post_delete'),
]
