from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('create_idea/', views.create_idea, name='create_idea'),
    path('view_idea/<int:idea_id>/', views.view_idea, name='view_idea'),
]
